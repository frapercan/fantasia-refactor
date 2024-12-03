import yaml
import os
import argparse
import subprocess
import sys


def die(message):
    """Print error message and exit."""
    sys.stderr.write(f"ERROR: {message}\n")
    sys.exit(1)


def load_config(config_file):
    """Load parameters from a YAML configuration file."""
    if not os.path.exists(config_file):
        die(f"Configuration file '{config_file}' does not exist.")
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def resolve_path(base, relative_path):
    """Resolve a relative path with a base directory."""
    return os.path.join(base, relative_path)


def main():
    parser = argparse.ArgumentParser(description="Generate input files for GOPredSim.")
    parser.add_argument("-c", "--config", required=True, help="Path to the configuration YAML file.")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Extract base directories
    base_dirs = config['base_directories']
    project_root = base_dirs['project_root']
    scripts_dir = resolve_path(project_root, base_dirs['scripts'])
    data_dir = resolve_path(project_root, base_dirs['data'])
    results_dir = resolve_path(project_root, base_dirs['results'])
    config_dir = resolve_path(project_root, base_dirs['config'])

    # Resolve paths for parameters
    infile = resolve_path(project_root, config['parameters']['infile'])
    outpath = resolve_path(project_root, config['parameters']['outpath'])
    prefix = config['parameters']['prefix']
    mode = config['parameters']['mode']
    seqvec = config['parameters']['models']['seqvec']
    prott5 = config['parameters']['models']['prott5']

    # Validate inputs
    if not os.path.isfile(infile):
        die(f"Input file '{infile}' does not exist.")
    if not os.path.isdir(outpath):
        os.makedirs(outpath)

    # Load script paths
    cd_hit_script = resolve_path(scripts_dir, "cd_hit_100.sh")
    remove_5k_script = resolve_path(scripts_dir, "remove_larger5k_prots.sh")
    create_yml_script = resolve_path(scripts_dir, "create_yml.py")

    # Step 1: Run CD-HIT
    cdhit_output = f"{os.path.splitext(infile)[0]}_cdhit100.pep"
    run_shell_command(f"bash {cd_hit_script} {infile} {cdhit_output}")

    if prott5:
        # Step 2: Remove sequences >5k
        prott5_output = f"{os.path.splitext(cdhit_output)[0]}_5k_removed.pep"
        run_shell_command(f"bash {remove_5k_script} {cdhit_output} {prott5_output}")

    # Step 3: Remove ending asterisks
    run_shell_command(f"sed -i 's/*//g' {cdhit_output}*")

    # Step 4: Create config files folders
    create_directories(config_dir)

    seqvec_input = os.path.realpath(cdhit_output)
    prott5_input = os.path.realpath(prott5_output) if prott5 else None

    # Step 5: Run Python script
    create_yml_command = [
        "python", create_yml_script,
        "-n", prefix,
        "-o", outpath,
        "-g", project_root,
        "-c", os.path.join(config_dir, "config_files"),
        "-m", mode
    ]

    if seqvec:
        create_yml_command.extend(["-s", seqvec_input])
    if prott5:
        create_yml_command.extend(["-p", prott5_input])

    run_shell_command(" ".join(create_yml_command))


def create_directories(config_path):
    """Create necessary directories if they don't exist."""
    embeddings_path = os.path.join(config_path, "config_files", "embeddings")
    gopredsim_path = os.path.join(config_path, "config_files", "gopredsim")
    os.makedirs(embeddings_path, exist_ok=True)
    os.makedirs(gopredsim_path, exist_ok=True)


def run_shell_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        die(f"Command failed: {command}")


if __name__ == "__main__":
    main()
