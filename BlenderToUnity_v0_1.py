bl_info = {
    "name": "BlenderToUnity",
    "author": "BoaKim",
    "version": (0,1),
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import bpy
import os
from bpy.props import StringProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

class ExportCollectionMeshesSettings(PropertyGroup):
    export_path: StringProperty(
        name="Export Path",
        description="Path to the folder where the meshes will be exported",
        default="",
        maxlen=512,
        subtype='DIR_PATH',
    )
    prefix: StringProperty(
        name="Prefix",
        description="Prefix for the exported file names",
        default="",
        maxlen=30,
    )

class ExportCollectionMeshesOperator(Operator):
    bl_idname = "object.export_collection_meshes"
    bl_label = "Export Collection Meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.export_collection_meshes_settings
        export_path = settings.export_path
        prefix = settings.prefix

        if not export_path:
            self.report({'WARNING'}, "No export path set.")
            return {'CANCELLED'}

        export_collection = bpy.data.collections.get("export")
        if not export_collection:
            self.report({'WARNING'}, "No collection named 'export' found.")
            return {'CANCELLED'}

        # Save the current selection
        saved_selection = context.selected_objects

        for obj in export_collection.objects:
            if obj.visible_get() and (obj.type == 'MESH' or obj.type == 'EMPTY'):
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                original_name = obj.name  # Store the original name

                bpy.ops.object.duplicate()
                duplicated_obj = context.active_object
                duplicated_obj.name = obj.name.split('.')[0]   
      
                # Apply the scale
                if obj.type == 'MESH':
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                # Export the objects
                export_file = os.path.join(export_path, f"{prefix}{obj.name.split('.')[0]}.fbx")
                bpy.ops.export_scene.fbx(
                    filepath=export_file,
                    use_selection=True,
                    use_active_collection=False,
                    global_scale=1.0,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    bake_space_transform=True,
                    use_mesh_modifiers=True,
                    use_mesh_edges=False,
                    use_tspace=False,
                    use_custom_props=False,
                    path_mode='AUTO',
                    embed_textures=False,
                    batch_mode='OFF',
                    use_batch_own_dir=True,
                    use_metadata=True,
                    axis_forward='Z',
                    axis_up='Y'
                )

                # Delete the duplicated object
                bpy.ops.object.delete()

                # Restore the original name
                obj.name = original_name

        # Restore the previous selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in saved_selection:
            obj.select_set(True)

        return {'FINISHED'}


class ExportPosOperator(Operator):
    bl_idname = "object.export_pos"
    bl_label = "Export Pos"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.export_collection_meshes_settings
        export_path = settings.export_path
        prefix = settings.prefix

        if not export_path:
            self.report({'WARNING'}, "No export path set.")
            return {'CANCELLED'}

        pos_collection = bpy.data.collections.get("Pos")
        if not pos_collection:
            self.report({'WARNING'}, "No collection named 'Pos' found.")
            return {'CANCELLED'}

        cubes = []
        if not pos_collection.objects:
            self.report({'WARNING'}, "No objects found in 'Pos' collection.")
            return {'CANCELLED'}

        # Store the visibility state of the Pos collection
        pos_collection_visibility = pos_collection.hide_viewport

        # Hide the Pos collection
        pos_collection.hide_viewport = True

        cubes = []
        if not pos_collection.objects:
            self.report({'WARNING'}, "No objects found in 'Pos' collection.")
            return {'CANCELLED'}
        
        for obj in pos_collection.objects:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cube_add()
            cube = context.active_object
            cube.name = obj.name
            cube.matrix_world = obj.matrix_world
            cube.location.x *= -1
            cube.location.y *= -1
            
            cubes.append(cube)

        bpy.ops.object.select_all(action='DESELECT')
        for cube in cubes:
            cube.select_set(True)

        export_file = os.path.join(export_path, f"Position.fbx")
        bpy.ops.export_scene.fbx(
            filepath=export_file,
            use_selection=True,
            use_active_collection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            bake_space_transform=True,
            use_mesh_modifiers=True,
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=True,
            axis_forward='-Z',
            axis_up='Y'
        )

        bpy.ops.object.select_all(action='DESELECT')
        for cube in cubes:
            cube.select_set(True)
        bpy.ops.object.delete()

        # Restore the visibility state of the Pos collection
        pos_collection.hide_viewport = pos_collection_visibility

        return {'FINISHED'}


class ExportCollectionMeshesPanel(Panel):
    bl_label = "Blender To Unity"
    bl_idname = "OBJECT_PT_blender to unity"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blender To Unity'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.export_collection_meshes_settings

        layout.prop(settings, "export_path")
        layout.prop(settings, "prefix")
        layout.operator(ExportCollectionMeshesOperator.bl_idname)
        layout.operator(ExportPosOperator.bl_idname)

def register():
    bpy.utils.register_class(ExportCollectionMeshesSettings)
    bpy.utils.register_class(ExportCollectionMeshesOperator)
    bpy.utils.register_class(ExportPosOperator)
    bpy.utils.register_class(ExportCollectionMeshesPanel)
    bpy.types.Scene.export_collection_meshes_settings = PointerProperty(type=ExportCollectionMeshesSettings)

def unregister():
    bpy.utils.unregister_class(ExportCollectionMeshesSettings)
    bpy.utils.unregister_class(ExportCollectionMeshesOperator)
    bpy.utils.unregister_class(ExportPosOperator)
    bpy.utils.unregister_class(ExportCollectionMeshesPanel)
    del bpy.types.Scene.export_collection_meshes_settings

if __name__ == "__main__":
    register()
