# WIDTH=20
# HEIGHT=15
# ENTRY=0,0
# EXIT=19,14
# OUTPUT_FILE=maze.txt
# PERFECT=True

# Criei uma classe Configuration para armazenar as configurações do labirinto

class Configuration():
    def __init__(self):
        self.width = -1
        self.height = -1
        self.entry = (-1, -1)
        self.exit = (-1, -1)
        self.output_file = ""
        self.perfect = None

#A parse_coordinates é necessária pra converter os valores do entry e exit pra tupla de ints, e validar que estão no formato correto. Se não tivere, vai dar erro
def parse_coordinates(value):
    x, y = value.split(",")
    return (int(x.strip()), int(y.strip()))

#A parser_config é necessária pra pegar o arquivo de configuração lido, transformar num dicionário de chave e valor, e  retornar esse dicionário
def parser_config(conf_file):
    confs = {}
    for line in conf_file.splitlines():
        if line.strip() and not line.startswith("#"):
            key, value = line.split("=", 1)
            if key.strip() in confs:
                raise ValueError(f"Duplicate configuration key: {key.strip()}")
            confs[key.strip()] = value.strip()
    return confs

# a validate_config é necessária pra validar os valores do dicionário de configuração, e retornar um objeto Configuration com os valores validados. Se algum valor for inválido, ele vai imprimir o erro e retornar o objeto Configuration com os valores padrão 
def validate_config(config: dict) -> Configuration:
    configuration = Configuration()
    try:
        for key, value in config.items():
            if key == "WIDTH":
                configuration.width = int(value)
            elif key == "HEIGHT":
                configuration.height = int(value)
            elif key == "ENTRY":
                configuration.entry = parse_coordinates(value)
            elif key == "EXIT":
                configuration.exit = parse_coordinates(value)
            elif key == "OUTPUT_FILE":
                configuration.output_file = value
            elif key == "PERFECT":
                if value.lower() not in ["true", "false"]:
                    raise ValueError("PERFECT must be 'true' or 'false'")
                configuration.perfect = value.lower() == "true"
            else:
                raise ValueError(f"Unknown configuration key: {key}")
    except Exception as e:
        print(f"Error validating config: {e}")
    return configuration

#por fim, a read_config_file é necessária pra ler o arquivo de configuração, chamar as funções de parser e validação, e retornar o objeto Configuration com os valores validados.
def read_config_file() -> Configuration:
    conf_dict = {}
    conf = None
    try:
        with open("config.txt") as file:
            conf_file = file.read()
        conf_dict = parser_config(conf_file)
        conf = validate_config(conf_dict)
    except Exception as e:
        print(f"Error: {e}")
    return conf

#TODO:
    # criar função para validar os valores de cada configuração, por exemplo, verificar se width e height são números positivos, se entry e exit estão dentro dos limites do labirinto, etc.
    # criar função para validar se o arquivo de saída é um caminho válido e se a extensão é .txt

if __name__ == "__main__":
    read_config_file()
