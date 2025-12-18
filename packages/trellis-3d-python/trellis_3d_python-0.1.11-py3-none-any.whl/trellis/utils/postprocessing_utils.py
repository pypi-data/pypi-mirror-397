from ..paint3d.DifferentiableRenderer.mesh_utils import convert_obj_to_glb
import tempfile
import os
import trimesh

def to_glb(
    mesh,
    simplify: float = 0.95,
    fill_holes: bool = True,
    fill_holes_max_size: float = 0.04,
    texture_size: int = 1024,
    debug: bool = False,
    verbose: bool = True,):

    # 创建临时 glb 文件
    with tempfile.NamedTemporaryFile(suffix=".glb", delete=False) as f:
        tmp_glb = f.name

    convert_obj_to_glb('textured_mesh.obj', tmp_glb)
    mesh = trimesh.load(tmp_glb, force="mesh")
    
    # thumb
    image = get_image(tmp_glb)
    
    # 用完删除（可选）
    os.remove(tmp_glb)
    
    return [mesh, image, 0]


def to_thumbnail(gaussian):

    

    return ''

def to_stl(v, f):

    return ''

def to_gif(gaussian):
    
    return ''

def get_image(glb_path):
    
    import bpy
    import math
    import mathutils

    # 新建干净场景
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb_path)

    # -----------------------------
    # 计算场景中心和尺寸
    # -----------------------------
    all_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    min_corner = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    max_corner = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in all_objects:
        for v in obj.bound_box:
            # bound_box 给的是局部坐标，需要转换为世界坐标
            coord = obj.matrix_world @ mathutils.Vector(v)
            min_corner.x = min(min_corner.x, coord.x)
            min_corner.y = min(min_corner.y, coord.y)
            min_corner.z = min(min_corner.z, coord.z)
            max_corner.x = max(max_corner.x, coord.x)
            max_corner.y = max(max_corner.y, coord.y)
            max_corner.z = max(max_corner.z, coord.z)

    center = (min_corner + max_corner) / 2
    size = max(max_corner - min_corner)  # 最大边长

    # -----------------------------
    # 创建相机
    # -----------------------------
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    # 相机位置：沿 +Y 轴偏离一定距离
    distance = size * 1.5
    cam_obj.location = center + mathutils.Vector((0, -distance, size/2))
    cam_obj.rotation_euler = (math.radians(75), 0, 0)
    bpy.context.scene.camera = cam_obj

    # -----------------------------
    # 添加光源
    # -----------------------------
    light_data = bpy.data.lights.new("Light", type='SUN')
    light_obj = bpy.data.objects.new("Light", light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = center + mathutils.Vector((distance/2, -distance/2, distance))
    light_obj.rotation_euler = (math.radians(60), 0, math.radians(45))

    out_png = "thumb.png"

    # -----------------------------
    # 渲染设置
    # -----------------------------
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'  # 或 'BLENDER_EEVEE'
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.filepath = out_png

    # 渲染并保存
    bpy.ops.render.render(write_still=True)

    from PIL import Image

    # 直接打开 PNG 文件
    image = Image.open("thumb.png")

    return image