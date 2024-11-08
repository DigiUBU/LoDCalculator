# Import libraries
import bpy, bmesh, csv, math, os
import numpy as np
import statistics as st
from bpy import context
import builtins as __builtin__

# Add-on information
bl_info = {
    "name": "LoDCalculator",
    "author": "XRAILab",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Scene Properties > LoDCalculator",
    "description": "Calculate the level of detail of an object on a scale of 1 to 5. Separate the score between radiometric and geometric fidelity, both on a scale of 1 to 3",
    "warning": "Only the selected object is evaluated. It is necessary that the object is not triangulated for the data to be reliable. Unused materials or textures need to be removed for the data to be reliable.",
    "doc_url": "https://xrailab.es/cases/lod-calculator/#1730711203073-09568c7b-2f57",
    "category": "",
}

# LoDCalculator class
class LoDCalculator(bpy.types.Operator):
    """Calculate the level of detail of an object"""
    bl_idname = "object.calcular_lod_operator"
    bl_label = "Calculate Result"
    
    # Initialize class variables
    final_puntuaction = 0
    geometrical_fidelity = 0
    last_interquartile_range = 0 
    mean_angle = 0
    face_number = 0
    loose_parts = 0
    proportion_of_faces = 0
    radiometrical_fidelity=0
    pixel_density_punctuation = 0
    material_quality_puntuation = 0
    proportion_materials_images = 0
    pixel_density = 0
    average_UV_area = 0
    average_resolution = 0
    number_textures = 0
    number_materials = 0
    tiled_percentaje = 0
    total_resolution = 0
    error = "none"

    # Execute main function of LoDCalculator
    def execute(self, context):
        
        # Check if there are selected objects
        selected_objects = bpy.context.selected_objects
        obj = bpy.context.active_object
        
        if not selected_objects:
            error = "No object selected"
            LoDCalculator.error = error
            return {'CANCELLED'}
        
        # Check if the selected object is of type mesh
        if obj.type != 'MESH':
            error = "Selected object is not a mesh"
            LoDCalculator.error = error
            return {'CANCELLED'}
        # OBTAINING GEOMETRIC INFORMATION
        
        # Import mesh data and count the faces
        rows = []
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = bpy.context.active_object
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        obj = bpy.context.active_object
        mesh = obj.data
        face_number = len(mesh.polygons)
        
        # Data collection
        # If the object is not 3D it does not get the data and assigns them
        if face_number < 2:
            error = "The selected object is not 3D, for a correct analysis, at least 2 faces are needed"
            mean_angle = 0
            last_interquartile_range = 0
        # If the object is 3D, it obtains the data
        else:
            error = "none"
            # iterate all geometry
            for i, e in enumerate(bm.edges):
                # Calculates the difference of angles between faces rounded to two decimal places
                angle = round(e.calc_face_angle_signed(10), 1000000)
                # Save the data
                rows.append([i, angle])
            bm.free()
            
            # Data processing
            data = [i for i in rows if i!=[]]
            data2 = []
            for i in data:
                # Convert all angles to absolute 
                aux = round(abs(math.degrees(float(i[1]))),2)
                # Remove the errors
                if aux!=572.96:
                    # Move all angles to the first quadrant
                    if aux > 90:
                        aux = 180-aux
                    data2.append(round(aux,2))
                    
            # Calculates the final data to be used in scores
            data_array = np.array(data2)
            # Calculate the average
            mean_angle= round(np.mean(data_array),2)
            # Organize angles from 0 to 90 into quartiles
            quartiles = np.concatenate(([np.min(data_array)],np.quantile(data_array,[0.25,0.5,0.75]),[np.max(data_array)]))
            # Calculates the path of the last interquartile range.
            last_interquartile_range = 90 - quartiles [3]
        
        # Count loose parts
        obj = bpy.context.active_object
        # Switches to edit mode and separates the object into loose parts
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        # Counts the loose parts and stores them
        separated_objects = [o for o in bpy.context.scene.objects if o.select_get()]
        loose_parts = len(separated_objects)
        # Join the loose parts
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for o in separated_objects:
            o.select_set(True)
        bpy.context.view_layer.objects.active = separated_objects[0]
        bpy.ops.object.join()
    
        # Calculate the ratio of faces per part
        proportion_of_faces = face_number / loose_parts  
        
     
        
        # OBTAINING RADIOMETRICAL INFORMATION
        
        # Calculate average size of textures and count the number of materials and textures
        # Initialize variables
        obj = bpy.context.selected_objects[0]
        number_materials = len(obj.material_slots)  
        obj = bpy.context.selected_objects[0]       
        # Remove materials without nodes
        for i in range(len(obj.data.materials) - 1, -1, -1):
            material = obj.data.materials[i]
            if not material or not material.use_nodes:
                obj.data.materials.pop(index=i)        
        # If the object has at least one material execute the code 
        if number_materials >= 1:
            material_slots = obj.material_slots
            number_textures = 0
            total_resolution = 0
            average_resolution = 0
            for material_slot in material_slots:        
                material = material_slot.material
                # Tries to search in the node tree, if there are no nodes launch the exception
                try:
                    # Search the image textures in the nodes
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            number_textures += 1
                            # Calculate average image pixels on one axis
                            resolution = math.sqrt(node.image.size[0] * node.image.size[1])
                            # Calculate the total size of the images
                            total_resolution += resolution
                    
                    # Calculate average size of images and initialize the variable
                    if number_textures > 0:
                         average_resolution = total_resolution / number_textures
                    # If there are no textures set the resolution to 0
                    else:
                         LoDCalculator.average_resolution = 0
                # Launch the expeption if there are empty material slots
                except Exception as e:
                    error = "The object has empty material slots, they have been deleted to obtain the results, but it is necessary to run the result again to have the updated data.."
        # If there are no materials set the score to 0      
        else:
            number_textures = 0
            error = "The selected object has not textures or materials"
            average_resolution = 0
        
        # Calculate the proportion of images by material
        if number_textures != 0:
                proportion_materials_images = round(number_textures/number_materials,2)
        else:
                proportion_materials_images = 1
        
        
        # Calculate pixel density
        # Access the object mesh
        obj = bpy.context.active_object
        mesh = obj.data
        # Access the UVs
        uv_layer = mesh.uv_layers.active
        # Initialize related variables
        total_uv_area = 0
        tiled_face = 0
        # Iteration for each polygon of the mesh to calculate the space of its UVs
        # If the object doesn't have UVs, assign the scores
        for poly in mesh.polygons:
            if len(obj.data.uv_layers) == 0:
               average_uv_area = 0
               tiled_face = 0
               error = "The object has no UVs"
            else:
            # Iterate each vertex
                uv_coords = [uv_layer.data[i].uv for i in poly.loop_indices]
                # Calculate the diameter of the two farthest vertices of each face
                diameter = max([(p1 - p2).length for p1 in uv_coords for p2 in uv_coords])
                # Calculate the minimum circular area of ​​each face and reduces it to the area of ​​a square embedded in it
                uv_area = 2*((diameter/2)*(diameter/2))
                # If the area is greater than 1.2, it is reduced to one to avoid increasing areas due to tiled faces and count how many faces are tiled
                if uv_area > 1.2:
                    uv_area = 1
                    tiled_face += 1
                # Calculate the total area 
                total_uv_area += uv_area 
        # Calculate the average area unwraped by dividing the total area by the number of faces
        average_uv_area = total_uv_area / face_number

        
        # Calculate the pixel density of the object by multiplying the average size of the textures by the average area of ​​the faces, then multiplies it by the number of faces by part 
        if (number_textures < 1) and (number_textures != 1): 
            pixel_density = 0
        else:    
            pixel_density=((average_resolution * average_uv_area ) * (proportion_of_faces) ) 
            
        if (number_materials < 1): 
            pixel_density = 0
        else:    
            pixel_density=((average_resolution * average_uv_area ) * (proportion_of_faces) )
            
        # Calculate the tile percentage
        tiled_percentaje = (tiled_face / face_number) * 100
    


        # CALCULATE THE FINAL SCORES
        
        # Geometrical score
        
        # If the object is extremely low poly, the score will always be 1.
        if proportion_of_faces < 10:
            geometrical_fidelity = 1
        # Calculate the score
        else:
            if 0 < last_interquartile_range <= 20 and (mean_angle <= 35):
                geometrical_fidelity = 2
            elif (last_interquartile_range < 5) and (mean_angle <= 45):
                geometrical_fidelity = 2
            elif 0 < last_interquartile_range <= 20:
                geometrical_fidelity = 1
            elif 20 < last_interquartile_range < 40 and (mean_angle <= 25):
                geometrical_fidelity = 3
            elif 20 < last_interquartile_range < 40:
                  geometrical_fidelity = 2
            elif last_interquartile_range >= 40 and (mean_angle > 40): 
                geometrical_fidelity = 2
            elif last_interquartile_range >= 40: 
                geometrical_fidelity = 3
            elif (last_interquartile_range < 5) and (mean_angle >= 45):
                geometrical_fidelity = 1
            
                                
        # Radiometrical scores
        
        # Material proportion score
        # If the object has no materials, the score will always be 1.
        if number_materials < 1:
            error = "The selected object has not materials"
            material_quality_puntuation = 1
         # Calculate the score   
        else:    
            if proportion_materials_images <= 1.1:
                material_quality_puntuation = 1
            elif 1.1 < proportion_materials_images <= 1.666:
                material_quality_puntuation = 2
            else:
                material_quality_puntuation = 3
        
        
        # Pixel density score
        # Calculate the score 
        if pixel_density <= 512:
            pixel_density_punctuation = 1
        else:
            if pixel_density > 512 and pixel_density <= 1500:
                 pixel_density_punctuation = 2
            elif pixel_density > 1500:
                pixel_density_punctuation = 3
        # If the percentage of tile is high, it subtracts score
        if (tiled_percentaje > 0.2) and (tiled_percentaje < 0.75) and (pixel_density_punctuation > 1):
            pixel_density_punctuation = pixel_density_punctuation -1
        elif (tiled_percentaje >= 0.75) and (pixel_density_punctuation == 3):
            pixel_density_punctuation = pixel_density_punctuation -2
        elif (tiled_percentaje >= 0.75) and (pixel_density_punctuation == 2):
             pixel_density_punctuation = pixel_density_punctuation -1
        
        
        # General radiometrical score
        radiometrical_fidelity= (pixel_density_punctuation + material_quality_puntuation) / 2
        
  

        # FINAL PUNCTUATION
        final_puntuaction = (radiometrical_fidelity + geometrical_fidelity) -1
        

        # Error combinations
        if (number_materials <1 ) and (number_textures < 1):
            error = "The selected object has not textures and materials"
        if (number_materials < 2) and (number_textures < 1):
            error = "The selected object has not textures"
        if (face_number < 2) and (number_textures < 1):
            error = "The selected object is not 3D and has not materials"   
        
        
        # STREAM THE VARIABLES TO THE UI
        LoDCalculator.final_puntuaction = final_puntuaction
        LoDCalculator. geometrical_fidelity = geometrical_fidelity
        LoDCalculator.last_interquartile_range = last_interquartile_range
        LoDCalculator.mean_angle = mean_angle
        LoDCalculator.face_number = face_number
        LoDCalculator.loose_parts = loose_parts
        LoDCalculator.proportion_of_faces = round(proportion_of_faces, 2)
        LoDCalculator.radiometrical_fidelity = radiometrical_fidelity
        LoDCalculator.pixel_density_punctuation = pixel_density_punctuation
        LoDCalculator.material_quality_puntuation = material_quality_puntuation
        LoDCalculator.proportion_materials_images = round(proportion_materials_images, 2)
        LoDCalculator.pixel_density = round(pixel_density, 2)
        LoDCalculator.average_UV_area = round(average_uv_area, 4)
        LoDCalculator.average_resolution = round(average_resolution, 2)
        LoDCalculator.number_textures = number_textures
        LoDCalculator.number_materials = number_materials
        LoDCalculator.tiled_percentaje = round (tiled_percentaje, 4)
        LoDCalculator.error = error
        
        # END OF THE CLASS
        return {'FINISHED'}    
        
        
# INTERFACE CLASS
class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "LoDCalculator"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    # layout function
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Create the result button  
        row = layout.row()
        row.scale_y = 3.0
        #execute LoDCalculator class
        row.operator("object.calcular_lod_operator" )      
         
        # Final punctuation row
        layout.label(text=" LoD Score:")
        row = layout.row()
        row.label(text=str(LoDCalculator.final_puntuaction)+ " out of 5")
        
        
        # Columuns of data
        split = layout.split()

        # Geometrical fidelity column
        col = split.column()
        col.label(text= "Geometric fidelity score: ")
        col.label(text=str(LoDCalculator. geometrical_fidelity) + " out of 3")

        col.label(text="Last interquartile range: ")
        col.label(text=str(round(LoDCalculator.last_interquartile_range, 2)))
        
        col.label(text="Mean angle: ")
        col.label(text=str(round(LoDCalculator.mean_angle, 2)))
        
        col.label(text="Number of faces: ")
        col.label(text=str(LoDCalculator.face_number))
        
        col.label(text="Number of meshes: ")
        col.label(text=str(LoDCalculator.loose_parts))
        
        col.label(text="Faces by mesh: ")
        col.label(text=str(round(LoDCalculator.proportion_of_faces, 2)))
        
        # Radiometrical fidelity column
        col = split.column(align=True)
        col.label(text="Radiometrical Fidelity score: ")
        col.label(text=str(LoDCalculator.radiometrical_fidelity)+ " out of 3")
        
        col.label(text="Average UV area by face: ")
        col.label(text=str(round(LoDCalculator.average_UV_area, 4)))
        
        col.label(text="Percentaje of tiled faces: ")
        col.label(text=str(round(LoDCalculator.tiled_percentaje, 2)))
        
        col.label(text="Average textures resolution: ")
        col.label(text=str(round(LoDCalculator.average_resolution, 2)))
        
        col.label(text="Number of textures: ")
        col.label(text=str(LoDCalculator.number_textures))
        
        col.label(text="Number of materials: ")
        col.label(text=str(LoDCalculator.number_materials))
        
        col.label(text="Textures by material: ")
        col.label(text=str(round(LoDCalculator.proportion_materials_images, 2)))
    
        # Error notice row
        layout.label(text="Error notification:")
        row = layout.row()
        row.label(text=str(LoDCalculator.error))

# Register all classes
def register():
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(LoDCalculator)
    
def unregister():
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(LoDCalculator)

if __name__ == "__main__":
    register()    
    

