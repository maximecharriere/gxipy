from gxipy.gxiapi import *

class Buffer:
    def __init__(self, data_array):
        try:
            addressof(data_array)
        except TypeError:
            error_msg = "Buffer.__init__: param is error type."
            raise ParameterTypeError(error_msg)

        self.data_array = data_array

    @staticmethod
    def from_file(file_name):
        file_object = open(file_name, "rb")
        file_string = file_object.read()
        # print("data_array_len0:", len(file_string))
        data_array = create_string_buffer(file_string,len(file_string))
        # print("data_array_len:",len(data_array))
        # print("data_array:",data_array)
        file_object.close()
        return Buffer(data_array)

    @staticmethod
    def from_string(string_data):
        data_array = create_string_buffer(string_data, len(string_data))
        return Buffer(data_array)

    def get_data(self):
        buff_p = c_void_p()
        buff_p.value = addressof(self.data_array)
        string_data = string_at(buff_p, len(self.data_array))
        return string_data

    def get_ctype_array(self):
        return self.data_array

    def get_numpy_array(self):
        numpy_array = numpy.array(self.data_array)
        return numpy_array

    def get_length(self):
        return len(self.data_array)