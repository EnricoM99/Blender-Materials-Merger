bl_info = {
    "name": "Merge Identical Materials by Data",
    "author": "Erik Marberg",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "File > External Data > Merge Identical Textures",
    "description": "Merges identical textures across materials",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import hashlib
from collections import defaultdict

def get_image_hash(image):
    pixels = list(image.pixels)
    pixel_data = bytes([int(p * 255) for p in pixels])
    return hashlib.md5(pixel_data).hexdigest()

def merge_materials_operator(self, context):
    def merge_node_based_materials():
        image_hashes = {}
        material_users = defaultdict(list)

        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue

            img_hash = None

            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    img = node.image
                    if img.name not in image_hashes:
                        image_hashes[img.name] = get_image_hash(img)
                    img_hash = image_hashes[img.name]
                    break

            if img_hash:
                material_users[img_hash].append(mat)

        merged_materials = 0
        for materials in material_users.values():
            if len(materials) > 1:
                primary_mat = materials[0]
                for mat in materials[1:]:
                    for obj in bpy.data.objects:
                        for slot in obj.material_slots:
                            if slot.material == mat:
                                slot.material = primary_mat
                                merged_materials += 1

        unused_materials = 0
        for mat in bpy.data.materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
                unused_materials += 1

        return merged_materials, unused_materials

    merged_materials, unused_materials = merge_node_based_materials()
    self.report({'INFO'}, f"Finished processing! Merged materials: {merged_materials}, Unused materials removed: {unused_materials}")

class MergeMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.merge_materials"
    bl_label = "Merge Materials by Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        merge_materials_operator(self, context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MergeMaterialsOperator.bl_idname)

def register():
    bpy.utils.register_class(MergeMaterialsOperator)
    bpy.types.TOPBAR_MT_file_external_data.prepend(menu_func)

def unregister():
    bpy.utils.unregister_class(MergeMaterialsOperator)
    bpy.types.TOPBAR_MT_file_external_data.remove(menu_func)

if __name__ == "__main__":
    register()
