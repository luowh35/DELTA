import logging

def setup_logging():
    logging.basicConfig(
        filename='Generation.log',
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

def display_info():
    info = """
    =====================================================================================
     DELTA: Differential Evolution Algorithm for Large-scale Tailored Atomistic Structures
     Version: 0.0.1
     arthor: Wenhao Luo
     Description: A Package for searching min Energy for Large-scale Atomistic Structures
    =====================================================================================
    """
    logo = """
   _ .-') _     ('-.            .-') _      ('-.     
  ( (  OO) )  _(  OO)          (  OO) )    ( OO ).-. 
   \     .'_ (,------.,--.     /     '._   / . --. / 
   ,`'--..._) |  .---'|  |.-') |'--...__)  | \-.  \  
   |  |  \  ' |  |    |  | OO )'--.  .--'.-'-'  |  | 
   |  |   ' |(|  '--. |  |`-' |   |  |    \| |_.'  | 
   |  |   / : |  .--'(|  '---.'   |  |     |  .-.  | 
   |  '--'  / |  `---.|      |    |  |     |  | |  | 
   `-------'  `------'`------'    `--'     `--' `--' 
    """
    logging.info(info)
    logging.info(logo)
