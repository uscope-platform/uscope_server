import fCore_has_py as has

class CompilerBridge:

    def compile(self, file_content: str):
        try:
            program_content, program_size = has.fCore_has_embeddable_s(file_content)
            return program_content, program_size
        except RuntimeError as error:
            raise ValueError(str(error).split('runtime_error: ')[1])




