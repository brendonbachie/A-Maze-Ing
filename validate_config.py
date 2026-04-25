# WIDTH=20
# HEIGHT=15
# ENTRY=0,0
# EXIT=19,14
# OUTPUT_FILE=maze.txt
# PERFECT=True

# Criei uma classe Configuration para armazenar as configurações do labirinto

class Configuration():
    def __init__(self) -> None:
        # verificar se os valores são negativos (width e height)
        self.width = -1
        self.height = -1
        # verificar se os valores são negativos ou se estão fora dos limites
        # do labirinto (entry e exit)
        self.entry = (-1, -1)
        self.exit = (-1, -1)
        # verificar se o valor é um caminho válido e se a extensão é .txt
        # (output_file)
        self.output_file = ""
        # verificar se o valor é 'true' ou 'false' (perfect)
        self.perfect = True
        self.seed: int | None = None
        self.teseu: tuple[int, int] = (-1, -1)
        self.minotaur: tuple[int, int] = (-1, -1)
        self.gamemode = True


# A parse_coordinates é necessária pra converter os valores do entry e exit
# pra tupla de ints, e validar que estão no formato correto. Se não tiver,
# vai dar erro
def parse_coordinates(value: str, width: int, height: int) -> tuple[int, int]:
    x_str, y_str = value.split(",")
    x, y = int(x_str.strip()), int(y_str.strip())
    return (x, y)


# A parser_config é necessária pra pegar o arquivo de configuração lido,
# transformar num dicionário de chave e valor, e  retornar esse dicionário
def parser_config(conf_file: str) -> dict[str, str]:
    confs = {}
    for line in conf_file.splitlines():
        if line.strip() and not line.startswith("#"):
            key, value = line.split("=", 1)
            if key.strip() in confs:
                raise ValueError(f"Duplicate configuration key: {key.strip()}")
            confs[key.strip()] = value.strip()
    return confs


# a validate_config é necessária pra validar os valores do dicionário de
# configuração, e retornar um objeto Configuration com os valores validados.
# Se algum valor for inválido, ele vai imprimir o erro e retornar o objeto
# Configuration com os valores padrão
def validate_config(config: dict[str, str]) -> Configuration:
    configuration = Configuration()
    configs_required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                        "PERFECT"]
    try:
        for key, value in config.items():
            if key == "WIDTH" and int(value) > 0:
                configuration.width = int(value)
                configs_required.remove("WIDTH")
            elif key == "SEED" and int(value) > 0:
                configuration.seed = int(value)
            elif key == "HEIGHT" and int(value) > 0:
                configuration.height = int(value)
                configs_required.remove("HEIGHT")
            elif key == "ENTRY":
                configuration.entry = parse_coordinates(value,
                                                        configuration.width,
                                                        configuration.height)
                configs_required.remove("ENTRY")
            elif key == "EXIT":
                configuration.exit = parse_coordinates(value,
                                                       configuration.width,
                                                       configuration.height)
                configs_required.remove("EXIT")
            elif key == "TESEU":
                configuration.teseu = parse_coordinates(
                                                        value,
                                                        configuration.width,
                                                        configuration.height
                                                        )
            elif key == "MINOTAUR":
                configuration.minotaur = parse_coordinates(value,
                                                           configuration.width,
                                                           configuration.height
                                                           )
            elif key == "OUTPUT_FILE" and value.endswith(".txt"):
                configuration.output_file = value
                configs_required.remove("OUTPUT_FILE")
            elif key == "PERFECT":
                if value.lower() not in ["true", "false"]:
                    raise ValueError("PERFECT must be 'True' or 'False'")
                configuration.perfect = value.lower() == "true"
                configs_required.remove("PERFECT")
            elif key == "GAMEMODE":
                if value.lower() not in ["true", "false"]:
                    raise ValueError("GAMEMODE must be 'True' or 'False'")
                configuration.gamemode = value.lower() == "true"
            else:
                raise ValueError("Wrong configuration")
        if configs_required:
            raise ValueError(f"Missing configuration keys: \
{', '.join(configs_required)}")
    except Exception as e:
        print(f"Error validating config: {e}")
        exit(1)
    return configuration


# por fim, a read_config_file é necessária pra ler o arquivo de configuração,
# chamar as funções de parser e validação, e retornar o objeto Configuration
# com os valores validados.
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
        exit(1)
        if conf.x < 0 or conf.x >= conf.width:
            raise ValueError(f"X coordinate {conf.x} is out of bounds for \
            width {conf.width}")
        if conf.y < 0 or conf.y >= conf.height:
            raise ValueError(f"Y coordinate {conf.y} is out of bounds for \
            height {conf.height}")
    return conf


if __name__ == "__main__":
    config = read_config_file()
    print(f"Width: {config.width}")
    print(f"Height: {config.height}")
    print(f"Entry: {config.entry}")
    print(f"Exit: {config.exit}")
    print(f"Output File: {config.output_file}")
    print(f"Perfect: {config.perfect}")
