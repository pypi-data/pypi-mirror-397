from .__prelude__ import Qt
import os

class PureShader:
    def __init__(self, shader_type, shader_source):
        self.shader_type = shader_type
        self.shader_source = shader_source
    def compile(self, program: Qt.QOpenGLShaderProgram):
        program.addShaderFromSourceCode(self.shader_type, self.shader_source)

class Shader(PureShader):
    def __init__(self, shader_type: Qt.QOpenGLShader.ShaderTypeBit, shader_path: str):
        with open(os.path.join(os.path.dirname(__file__),shader_path)) as shader_file:
            shader_source = shader_file.read()
        super().__init__(shader_type, shader_source)
