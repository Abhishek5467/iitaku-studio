"""Original reusable Blender material templates. Toon is Eevee-only; bake for GLB."""
import bpy
def base(name):
    material=bpy.data.materials.get(name) or bpy.data.materials.new(name);material.use_nodes=True;material.node_tree.nodes.clear();nodes=material.node_tree.nodes;links=material.node_tree.links;out=nodes.new("ShaderNodeOutputMaterial");out.location=(600,0);return material,nodes,links,out

material,nodes,links,out=base("IITaku / PBR starter");shader=nodes.new("ShaderNodeBsdfPrincipled");shader.inputs["Base Color"].default_value=(.25,.12,.46,1);shader.inputs["Roughness"].default_value=.7;links.new(shader.outputs["BSDF"],out.inputs["Surface"])
material,nodes,links,out=base("IITaku / Neon starter");shader=nodes.new("ShaderNodeBsdfPrincipled");shader.inputs["Base Color"].default_value=(.05,.8,.45,1);shader.inputs["Emission Color"].default_value=(.05,1,.45,1);shader.inputs["Emission Strength"].default_value=3;links.new(shader.outputs["BSDF"],out.inputs["Surface"])
material,nodes,links,out=base("IITaku / Toon starter (Eevee)");diffuse=nodes.new("ShaderNodeBsdfDiffuse");rgb=nodes.new("ShaderNodeShaderToRGB");ramp=nodes.new("ShaderNodeValToRGB");ramp.color_ramp.interpolation="CONSTANT";ramp.color_ramp.elements[0].position=.3;ramp.color_ramp.elements[0].color=(.12,.08,.25,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.75,.48,.85,1);emission=nodes.new("ShaderNodeEmission");links.new(diffuse.outputs[0],rgb.inputs[0]);links.new(rgb.outputs[0],ramp.inputs[0]);links.new(ramp.outputs[0],emission.inputs[0]);links.new(emission.outputs[0],out.inputs["Surface"])
print("Created three material templates. Save your .blend file. Bake Eevee toon materials before glTF export.")
