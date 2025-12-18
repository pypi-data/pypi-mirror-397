import os
import sys
import numpy as np
import sympy
from tqdm import tqdm
import click

try:
    from ..model.models import PSRN
except (ImportError, ValueError):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    try:
        from psrn.model.models import PSRN
    except ImportError:
        raise ImportError("Could not import PSRN. Please install the package via 'pip install -e .' or run from root directory.")


def generate_dr_mask_core(n_symbol_layers, n_inputs, ops, save_dir="./dr_mask", device="cuda"):
    
    if isinstance(ops, str):
        if ops == "basic":
            ops = ["Add", "Mul", "Identity", "Neg", "Inv", "Sin", "Cos", "Exp", "Log"]
        elif ops == "koza":
            ops = ["Add", "Mul", "Sub", "Div", "Identity", "Neg", "Inv", "Sin", "Cos", "Exp", "Log"]
        elif ops == "basic_sign":
            ops = ["Add", "Mul", "Identity", "Neg", "Inv", "Sign"]
        elif ops == "koza_sign":
            ops = ["Add", "Mul", "Sub", "Div", "Identity", "Sign"]
        else:
            ops = eval(ops)
            
            if not isinstance(ops, list):
                raise ValueError(f"Ops must be a list, got {type(ops)}: {ops}")
    
    assert isinstance(ops, list), "ops must be a list of strings"

    input_variable_names = ["x{}".format(i + 1) for i in range(n_inputs)]
    n_layers = n_symbol_layers - 1
    
    psrn = PSRN(
        n_variables=len(input_variable_names),
        operators=ops,
        n_symbol_layers=n_layers,
        device=device,
    )

    psrn.current_expr_ls = input_variable_names
    out_expr_ls = []

    print(f"generating expressions (Layers={n_symbol_layers}, Inputs={n_inputs})...")
    for out_index in tqdm(range(psrn.out_dim), desc="Generating"):
        expr = psrn.get_expr(out_index)
        out_expr_ls.append(expr)

    print("sympifying ...")
    out_expr_sympy_ls = []
    for expr_str in tqdm(out_expr_ls, desc="Sympifying"):
        expr_sympy = sympy.sympify(expr_str)
        out_expr_sympy_ls.append(expr_sympy)

    out_expr_sympy_hash_ls = [hash(expr) for expr in out_expr_sympy_ls]

    def get_mask_ls():
        mask_ls = []
        select_expr_hash_ls = []
        for i in range(len(out_expr_sympy_hash_ls)):
            expr_hash = out_expr_sympy_hash_ls[i]
            if expr_hash not in select_expr_hash_ls:
                select_expr_hash_ls.append(expr_hash)
                mask_ls.append(True)
            else:
                mask_ls.append(False)
        return mask_ls

    print("removing duplicate expressions ...")
    mask_ls = get_mask_ls()
    mask_np = np.array(mask_ls)
    print("Final Expressions count:", mask_np.sum())

    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    ops_str_for_filename = "_".join(ops)
    file_name = f'{n_layers + 1}_{len(input_variable_names)}_[{ops_str_for_filename}]_mask.npy'
    
    save_path = os.path.join(save_dir, file_name)
    np.save(save_path, mask_np)
    print("Saved >>> {} <<<".format(save_path))
    
    return save_path


@click.command()
@click.option("--n_symbol_layers", type=int, help="Number of Symbol Layers.")
@click.option("--n_inputs", type=int, help="Number of PSRN Inputs.")
@click.option(
    "--ops",
    help="`basic` or `koza` or Operators List e.g. ['Add','Mul','Identity',...]",
)
@click.option("--save_dir", type=str, default="./dr_mask", help="Mask Save Dir")
@click.option("--gpu", type=str, default="0", help="GPU Index")
def main_cli(n_symbol_layers, n_inputs, ops, save_dir, gpu):
    """
    Command Line Interface Wrapper
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu
    
    generate_dr_mask_core(
        n_symbol_layers=n_symbol_layers,
        n_inputs=n_inputs,
        ops=ops,
        save_dir=save_dir,
        device="cuda"
    )

if __name__ == "__main__":
    main_cli()