from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import redis, json

############################################################
#                      IMPLEMENTATION                      #
############################################################


registers_manager_bp = Blueprint('regusters_manager', __name__, url_prefix='/registers')


api = Api(registers_manager_bp)


class RegisterValue(Resource):
    @jwt_required()
    def get(self):
        pass

    @jwt_required()
    def post(self, peripheral):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.set_register_value(peripheral, registers_to_write['payload'])
        return '200'


class RegisterDescriptions(Resource):
    @jwt_required()
    def get(self, peripheral):
        return jsonify(current_app.register_mgr.get_registers_descriptions(peripheral))

    @jwt_required()
    def post(self):
        pass


class PeripheralsSpecs(Resource):
    @jwt_required()
    def get(self):
        return jsonify(current_app.register_mgr.get_all_peripherals())


class PeripheralsDigest(Resource):
    @jwt_required()
    def get(self):
        return current_app.register_mgr.get_peripherals_digest()


class RegistersBulkWrite(Resource):
    @jwt_required()
    def post(self):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.bulk_write(registers_to_write['payload'])
        return '200'


api.add_resource(RegisterValue, '/<string:peripheral>/value')
api.add_resource(RegisterDescriptions, '/<string:peripheral>/descriptions')
api.add_resource(PeripheralsSpecs, '/all_peripheral/descriptions')
api.add_resource(RegistersBulkWrite, '/bulk_write')
api.add_resource(PeripheralsDigest, '/digest')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class RegistersManager:

    def __init__(self, interface, store, redis_host):
        self.interface = interface
        self.store = store
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=0)

    def get_all_peripherals(self):
        """Returns all the peripherals present in the database

            Returns:
                List:list of peripherals in the database
           """
        return self.store.get_peripherals()

    def get_peripherals_digest(self):
        """Returns an hash of the jsonified peripherals list

            Returns:
                str:Digest of the peripherals present in the database
           """
        return self.store.get_peripherals_hash()

    def get_registers_descriptions(self, peripheral_name):
        """Returns the specification for the registers of the specified peripheral

            Parameters:
                peripheral_name: name of the peripheral whose registers need to be returned
            Returns:
                List:list of registers in the peripheral
           """

        app = json.loads(self.redis_if.get("chosen_application"))
        found = False
        for peripheral in app['peripherals']:
            if peripheral_name in peripheral['peripheral_id']:
                found = True
                parameters = self.store.get_peripherals()[peripheral['spec_id']]
                base_address = int(peripheral['base_address'], 0)

        if not found:
            raise ValueError("The component register file was not found")




        registers_values = {}
        for i in parameters['registers']:
            if ('R' in i['direction'] or 'r' in i['direction']) and not current_app.app_mgr.peripheral_is_proxied(peripheral_name):
                address = base_address + int(i['offset'], 0)
                if i['register_format'] == 'words':
                    registers_values[i['register_name']] = self.interface.read_register(address)
                else:
                    registers_values[i['register_name']] = self.interface.read_register(address)

            else:
                registers_values[i['register_name']] = 0

        return {'peripheral_name': parameters['peripheral_name'], 'registers': registers_values}

    def get_register_value(self, peripheral_name, register_name):
        pass

    def set_register_value(self, peripheral, register):
        """Writes to a specifier register

            Parameters:
                peripheral: name of the peripheral whose registers need to be returned
                register: dictionary containing the register name and value
        """
        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral), 0)
        if current_app.app_mgr.peripheral_is_proxied(peripheral):
            proxy_addr = int(current_app.app_mgr.get_peripheral_proxy_address(peripheral), 0)
            self.__set_proxied_register_value(register, base_address, proxy_addr)
        else:
            self.__set_direct_register_value(register, base_address)

    def bulk_write(self, registers):
        """ Perform a bulk register write operations

            Parameters:
                registers: List of dictionaries containing the details for a single register write
           """
        for i in registers:
            self.interface.write_register(i['address'], i['value'])


    #TODO: REFACTOR THESE METHODS AWAY, PUSHING THIS LOGIC TO THE CLIENT
    def __set_direct_register_value(self, register, base_address):
        """Writes to a register that is directly accessible through the CPU bus itself

            Parameters:
                register: dictionary containing the details of the register write to perform
                base_address: base address of the peripheral to write to
           """
        periph = register['peripheral']
        peripheral_registers = self.store.get_peripherals()[periph]['registers']
        for i in peripheral_registers:
            if i['ID'] == register['name'] or i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                print(f'DIRECT WRITE: writen: {value} to register at address: {hex(address)}')
                self.interface.write_register(address, value)

    def __set_proxied_register_value(self, register, base_address, proxy_addr):
        """Writes to a register that is not directly connected to the bus but needs to be spoken with through a proxy peripheral

            Parameters:
                register: dictionary containing the details of the register write to perform
                base_address: base address of the peripheral to write to
                proxy_addr: base address of the proxy peripheral
           """
        periph = register['peripheral']
        peripheral_registers = self.store.get_peripherals()[periph]['registers']
        for i in peripheral_registers:
            if i['ID'] == register['name'] or i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                print(f'PROXY WRITE: writen: {value} to register at address: {hex(address)} through proxy at address: {hex(proxy_addr)}')
                self.interface.write_proxied_register(proxy_addr, address, value)

    def __split_dword(self, val):
        """Splits a single 32 bit register value to two 16 bit field values

            Parameters:
                val: register value to be split
            Returns:
                Tuple: couple of field values

           """
        w1 = int(val & 0xffff)
        w2 = int((val >> 16) & 0xffff)
        return w1, w2
