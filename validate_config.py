"""Validação e leitura da configuração do labirinto.

Lê o arquivo de configuração, interpreta chaves e valores, valida limites
e retorna um objeto Configuration usado para inicializar o jogo.
"""

# WIDTH=20
# HEIGHT=15
# ENTRY=0,0
# EXIT=19,14
# OUTPUT_FILE=maze.txt
# PERFECT=True

# Criei uma classe Configuration para armazenar as configurações do labirinto

class Configuration():
    """Armazena configurações do labirinto lidas do arquivo.

    Os campos incluem dimensões, posições especiais, arquivo de saída,
    flags de comportamento e semente aleatória.
    """
    def __init__(self) -> None:
        """Inicializa valores padrão para a configuração."""
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
    """Converte uma string "x,y" em uma tupla de inteiros (x, y).

    Args:
        value: String contendo coordenadas separadas por vírgula.
        width: Largura usada para validação (não usada diretamente aqui).
        height: Altura usada para validação (não usada diretamente aqui).

    Returns:
        Tupla (x, y) com valores inteiros.
    """
    x_str, y_str = value.split(",")
    x, y = int(x_str.strip()), int(y_str.strip())
    return (x, y)


# A parser_config é necessária pra pegar o arquivo de configuração lido,
# transformar num dicionário de chave e valor, e  retornar esse dicionário
def parser_config(conf_file: str) -> dict[str, str]:
    """Analisa o conteúdo do arquivo de configuração e retorna um dicionário.

    Linhas comentadas ou vazias são ignoradas. Cada linha válida deve ser no
    formato KEY=VALUE. Chaves duplicadas acarretam ValueError.

    Args:
        conf_file: Conteúdo do arquivo de configuração como string.

    Returns:
        Dicionário mapeando chaves para valores como strings.
    """
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
    """Valida um dicionário de configuração e retorna um objeto Configuration.

    Verifica presença de chaves obrigatórias, valores dentro dos limites e
    coerência entre posições especiais. Em caso de erro, o programa é abortado.

    Args:
        config: Dicionário com chaves e valores do arquivo de configuração.

    Returns:
        Uma instância de Configuration com os valores validados.
    """
    configuration = Configuration()
    configs_required = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]
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
        coords_to_validate: list[tuple[str, tuple[int, int]]] = [
            ("ENTRY", configuration.entry),
            ("EXIT", configuration.exit),
        ]
        if configuration.gamemode:
            if configuration.teseu == configuration.minotaur:
                raise ValueError(
                    "TESEU and MINOTAUR cannot be at the same position"
                )
            coords_to_validate += [
                ("TESEU", configuration.teseu),
                ("MINOTAUR", configuration.minotaur),
            ]
        for name, (x, y) in coords_to_validate:
            if name in ["TESEU", "MINOTAUR"] and (x, y) == configuration.exit:
                raise ValueError(
                    f"{name} cannot be at the same position as EXIT"
                )
            if x < 0 or x >= configuration.width:
                raise ValueError(f"{name} X coordinate {x} out of bounds")
            if y < 0 or y >= configuration.height:
                raise ValueError(f"{name} Y coordinate {y} out of bounds")
    except Exception as e:
        print(f"Error validating config: {e}")
        exit(1)
    return configuration


# por fim, a read_config_file é necessária pra ler o arquivo de configuração,
# chamar as funções de parser e validação, e retornar o objeto Configuration
# com os valores validados.
def read_config_file() -> Configuration:
    """Lê o arquivo config.txt, faz parsing e validação, e retorna Configuration.

    Em caso de erro, imprime a mensagem e encerra o programa.

    Returns:
        Instância de Configuration com os valores validados.
    """
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
    return conf


if __name__ == "__main__":
    config = read_config_file()
    print(f"Width: {config.width}")
    print(f"Height: {config.height}")
    print(f"Entry: {config.entry}")
    print(f"Exit: {config.exit}")
    print(f"Output File: {config.output_file}")
    print(f"Perfect: {config.perfect}")
