#!/usr/bin/env python3
"""
Focused test script for DB-CBS with motion primitives.
This script is designed for testing motion primitive durations and basic DB-CBS functionality
without running the full benchmark suite.
"""

import yaml
import subprocess
from pathlib import Path
import argparse
import sys

def run_dbcbs_focused(env_file, result_folder, timelimit, config):
    """
    Run DB-CBS with the given configuration.
    This is a simplified version of main_dbcbs.run_dbcbs()
    """
    print(f"Running DB-CBS on {env_file}")
    print(f"Results will be saved to: {result_folder}")
    print(f"Time limit: {timelimit}s")
    print(f"Config: {config}")

    # Create result folder if it doesn't exist
    result_folder = Path(result_folder)
    result_folder.mkdir(parents=True, exist_ok=True)

    # Build the command to run db_cbs
    cmd = [
        "../buildRelease/db_cbs",
        "--env", str(env_file),
        "--result_file", str(result_folder / "result_dbcbs_opt.yaml"),
        "--timelimit", str(timelimit)
    ]

    # Add configuration parameters
    if "max_computation_time" in config:
        cmd.extend(["--max_computation_time", str(config["max_computation_time"])])
    if "suboptimality" in config:
        cmd.extend(["--suboptimality", str(config["suboptimality"])])
    if "motions" in config:
        cmd.extend(["--motions", str(config["motions"])])
    if "check_resolution" in config:
        cmd.extend(["--check_resolution", str(config["check_resolution"])])

    print(f"Running command: {' '.join(cmd)}")

    # Run the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timelimit + 10)

        # Save stdout and stderr to files
        with open(result_folder / "stdout.txt", 'w') as f:
            f.write(result.stdout)
        with open(result_folder / "stderr.txt", 'w') as f:
            f.write(result.stderr)

        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode != 0:
            print(f"WARNING: Command failed with return code {result.returncode}")
        else:
            print("DB-CBS completed successfully!")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out after {timelimit + 10} seconds")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run command: {e}")
        return False

def check_motion_primitives(motions_file):
    """
    Check if motion primitives file exists and print basic info about it.
    """
    motions_path = Path(motions_file)
    if not motions_path.exists():
        print(f"WARNING: Motion primitives file not found: {motions_file}")
        return False

    print(f"Motion primitives file found: {motions_file}")
    print(f"File size: {motions_path.stat().st_size} bytes")

    # Try to get more info if possible (this would require loading the .msgpack file)
    # For now, just check if it's a reasonable size
    if motions_path.stat().st_size > 0:
        print("Motion primitives file appears to be valid (non-empty)")
        return True
    else:
        print("WARNING: Motion primitives file is empty")
        return False

def create_simple_test_environment(output_file):
    """
    Create a simple test environment for quick testing.
    """
    env_config = {
        'environment': {
            'min_time': 0.0,
            'max_time': 10.0,
            'x_min': -5.0,
            'x_max': 5.0,
            'y_min': -5.0,
            'y_max': 5.0,
            'obstacles': []  # No obstacles for simple test
        },
        'robots': [
            {
                'type': 'dingo_differential_drive',
                'start': [0.0, 0.0, 0.0],  # x, y, theta
                'goal': [3.0, 3.0, 0.0]    # x, y, theta
            }
        ]
    }

    with open(output_file, 'w') as f:
        yaml.dump(env_config, f, default_flow_style=False)

    print(f"Created simple test environment: {output_file}")

def examine_motion_primitives(motions_file):
    """
    Examine the structure of a motion primitives file using msgpack.
    This helps understand the format and durations.
    """
    try:
        import msgpack
    except ImportError:
        print("ERROR: msgpack not installed. Install with: pip install msgpack")
        return False

    motions_path = Path(motions_file)
    if not motions_path.exists():
        print(f"ERROR: Motion primitives file not found: {motions_file}")
        return False

    print(f"\n=== EXAMINING MOTION PRIMITIVES: {motions_file} ===")
    print(f"File size: {motions_path.stat().st_size} bytes")

    try:
        with open(motions_path, 'rb') as f:
            data = msgpack.load(f)

        print(f"Data type: {type(data)}")

        if isinstance(data, dict):
            print(f"Keys in data: {list(data.keys())}")

            # Examine the data structure more deeply
            if 'data' in data:
                inner_data = data['data']
                print(f"Inner data type: {type(inner_data)}")
                if isinstance(inner_data, dict):
                    print(f"Inner data keys: {list(inner_data.keys())}")
                elif isinstance(inner_data, list):
                    print(f"Inner data is a list with {len(inner_data)} elements")
                    if len(inner_data) > 0:
                        print(f"First element type: {type(inner_data[0])}")
                        if isinstance(inner_data[0], dict):
                            print(f"First element keys: {list(inner_data[0].keys())}")

            # Look for common motion primitive fields
            if 'motions' in data:
                motions = data['motions']
                print(f"Number of motion primitives: {len(motions)}")

                if len(motions) > 0:
                    first_motion = motions[0]
                    print(f"First motion keys: {list(first_motion.keys()) if isinstance(first_motion, dict) else 'Not a dict'}")

                    # Look for duration information
                    duration_keys = ['duration', 'time', 'dt', 'time_step', 'T']
                    for key in duration_keys:
                        if key in first_motion:
                            print(f"Found duration field '{key}': {first_motion[key]}")

                    # Sample a few motions to see duration range
                    durations = []
                    sample_size = min(10, len(motions))
                    for i in range(sample_size):
                        motion = motions[i]
                        for key in duration_keys:
                            if key in motion:
                                durations.append(motion[key])
                                break

                    if durations:
                        print(f"Sample durations from first {sample_size} motions: {durations}")
                        print(f"Duration range: {min(durations):.3f} - {max(durations):.3f}")
                    else:
                        print("No duration information found in standard fields")
                        print("Motion structure example:")
                        if isinstance(first_motion, dict):
                            for key, value in list(first_motion.items())[:5]:  # Show first 5 fields
                                print(f"  {key}: {type(value)} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")

            # If no 'motions' key, check if data itself contains motion primitives
            elif 'data' in data:
                inner_data = data['data']
                if isinstance(inner_data, list) and len(inner_data) > 0:
                    print(f"Treating data list as motion primitives with {len(inner_data)} elements")
                    first_motion = inner_data[0]
                    if isinstance(first_motion, dict):
                        print(f"First motion keys: {list(first_motion.keys())}")

                        # Look for duration information
                        duration_keys = ['duration', 'time', 'dt', 'time_step', 'T']
                        for key in duration_keys:
                            if key in first_motion:
                                print(f"Found duration field '{key}': {first_motion[key]}")

                        # Sample a few motions to see duration range
                        durations = []
                        sample_size = min(10, len(inner_data))
                        for i in range(sample_size):
                            motion = inner_data[i]
                            if isinstance(motion, dict):
                                for key in duration_keys:
                                    if key in motion:
                                        durations.append(motion[key])
                                        break

                        if durations:
                            print(f"Sample durations from first {sample_size} motions: {durations}")
                            print(f"Duration range: {min(durations):.3f} - {max(durations):.3f}")
                        else:
                            print("No duration information found in standard fields")
                            print("Motion structure example:")
                            for key, value in list(first_motion.items())[:5]:  # Show first 5 fields
                                print(f"  {key}: {type(value)} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")

                            # Look deeper into actions and states to understand duration
                            if 'actions' in first_motion and 'states' in first_motion:
                                actions = first_motion['actions']
                                states = first_motion['states']
                                print("\nDetailed analysis:")
                                print(f"  Actions: {len(actions)} steps")
                                print(f"  States: {len(states)} steps")

                                if len(actions) > 0:
                                    print(f"  First action: {actions[0]} (type: {type(actions[0])})")
                                    if len(actions) > 1:
                                        print(f"  Second action: {actions[1]} (type: {type(actions[1])})")

                                if len(states) > 0:
                                    print(f"  First state: {states[0]} (type: {type(states[0])})")
                                    if len(states) > 1:
                                        print(f"  Second state: {states[1]} (type: {type(states[1])})")

                                # Check if there's a time field in states or if we can infer dt
                                if len(states) > 1 and isinstance(states[0], list) and len(states[0]) > 2:
                                    print(f"  State dimension: {len(states[0])}")
                                    print("  Assuming [x, y, theta, ...], first few states:")
                                    for i in range(min(3, len(states))):
                                        if isinstance(states[i], list) and len(states[i]) >= 3:
                                            print(f"    State {i}: x={states[i][0]:.3f}, y={states[i][1]:.3f}, theta={states[i][2]:.3f}")

                                # Estimated duration based on number of steps (need to know dt)
                                print(f"  Estimated motion primitive duration: {len(actions)} * dt seconds")
                                print("  (where dt is the simulation timestep, typically 0.01-0.1s)")
                elif isinstance(inner_data, dict):
                    print("Data contains a dictionary, checking for motion primitive fields...")
                    if 'motions' in inner_data:
                        motions = inner_data['motions']
                        print(f"Found motions in inner data with {len(motions)} primitives")
                        # Apply same analysis as above
                        if len(motions) > 0:
                            first_motion = motions[0]
                            if isinstance(first_motion, dict):
                                print(f"First motion keys: {list(first_motion.keys())}")
                                duration_keys = ['duration', 'time', 'dt', 'time_step', 'T']
                                for key in duration_keys:
                                    if key in first_motion:
                                        print(f"Found duration field '{key}': {first_motion[key]}")
                    else:
                        print(f"Inner data dict keys: {list(inner_data.keys())}")

            # Look for other relevant fields
            for key in ['dt', 'time_step', 'duration', 'robot_type']:
                if key in data:
                    print(f"Global {key}: {data[key]}")

        elif isinstance(data, list):
            print(f"Data is a list with {len(data)} elements")
            if len(data) > 0:
                print(f"First element type: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"First element keys: {list(data[0].keys())}")

        return True

    except Exception as e:
        print(f"ERROR reading motion primitives file: {e}")
        return False

def find_motion_primitive_files():
    """
    Find all motion primitive files in the project.
    """
    base_dir = Path("../")
    msgpack_files = []

    # Search in common locations
    search_paths = [
        base_dir / "dynoplan" / "dynomotions",
        base_dir / "dynoplan" / "dynobench" / "envs",
        base_dir / "dynoplan" / "data" / "motion_primitives"
    ]

    for search_path in search_paths:
        if search_path.exists():
            msgpack_files.extend(search_path.rglob("*.msgpack"))

    return sorted(msgpack_files)

def main():
    parser = argparse.ArgumentParser(description="Focused DB-CBS test script")
    parser.add_argument("--env", help="Environment file (.yaml)", default=None)
    parser.add_argument("--create_simple_env", help="Create a simple test environment", action="store_true")
    parser.add_argument("--result_folder", help="Results folder", default="./test_results")
    parser.add_argument("--timelimit", type=float, help="Time limit in seconds", default=30.0)
    parser.add_argument("--motions", help="Motion primitives file (.msgpack)", default=None)
    parser.add_argument("--suboptimality", type=float, help="Suboptimality factor", default=1.0)
    parser.add_argument("--check_resolution", type=float, help="Check resolution", default=0.1)
    parser.add_argument("--list_examples", help="List available example environments", action="store_true")
    parser.add_argument("--examine_motions", help="Examine a motion primitives file", default=None)
    parser.add_argument("--find_motions", help="Find all motion primitive files in the project", action="store_true")
    parser.add_argument("--explore_motions", help="Explore existing motion primitive files", action="store_true")

    args = parser.parse_args()

    # Change to the scripts directory (same as benchmark.py does)
    scripts_dir = Path(__file__).parent
    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(scripts_dir)

        if args.list_examples:
            example_dir = Path("../example")
            if example_dir.exists():
                print("Available example environments:")
                for yaml_file in example_dir.glob("*.yaml"):
                    if yaml_file.name != "algorithms.yaml":  # Skip config file
                        print(f"  {yaml_file.name}")
            else:
                print("Example directory not found")
            return

        if args.find_motions:
            print("Searching for motion primitive files...")
            motion_files = find_motion_primitive_files()
            if motion_files:
                print(f"Found {len(motion_files)} motion primitive files:")
                for mf in motion_files:
                    print(f"  {mf}")
                print("\nTo examine a specific file, use:")
                print(f"  python3 {Path(__file__).name} --examine_motions <file_path>")
            else:
                print("No motion primitive files found")
            return

        if args.examine_motions:
            success = examine_motion_primitives(args.examine_motions)
            if success:
                print("\nMotion primitive examination completed!")
            else:
                print("\nMotion primitive examination failed!")
            return

        # Create simple environment if requested
        if args.create_simple_env:
            simple_env_path = Path("../example/test_simple_dingo.yaml")
            simple_env_path.parent.mkdir(parents=True, exist_ok=True)
            create_simple_test_environment(simple_env_path)
            print(f"You can now run: python3 {Path(__file__).name} --env {simple_env_path}")
            return

        # Check environment file
        if not args.env:
            print("ERROR: No environment file specified. Use --env or --create_simple_env")
            print("Use --list_examples to see available environments")
            return

        env_path = Path(args.env)
        if not env_path.exists():
            print(f"ERROR: Environment file not found: {args.env}")
            return

        # Check motion primitives if specified
        if args.motions:
            if not check_motion_primitives(args.motions):
                print("Continuing anyway, but motion primitives may not work correctly...")
        else:
            print("No motion primitives file specified. DB-CBS will use kinodynamic model.")

        # Create configuration
        config = {
            "suboptimality": args.suboptimality,
            "check_resolution": args.check_resolution,
            "max_computation_time": args.timelimit
        }

        if args.motions:
            config["motions"] = args.motions

        print("=" * 60)
        print("FOCUSED DB-CBS TEST")
        print("=" * 60)

        # Run DB-CBS
        success = run_dbcbs_focused(env_path, args.result_folder, args.timelimit, config)

        if success:
            print("\n" + "=" * 60)
            print("TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)

            # Check for result files
            result_folder = Path(args.result_folder)
            result_files = list(result_folder.glob("result_*.yaml"))
            if result_files:
                print(f"Result files created: {[f.name for f in result_files]}")

                # Try to show basic stats from the result
                try:
                    with open(result_files[0]) as f:
                        result_data = yaml.safe_load(f)
                    if 'statistics' in result_data:
                        stats = result_data['statistics']
                        print("\nBasic Statistics:")
                        for key, value in stats.items():
                            print(f"  {key}: {value}")
                except Exception as e:
                    print(f"Could not parse result file: {e}")
            else:
                print("No result files found")
        else:
            print("\n" + "=" * 60)
            print("TEST FAILED!")
            print("=" * 60)
            print("Check the stdout.txt and stderr.txt files in the result folder for details.")

        # Explore motion primitives if requested
        if args.explore_motions:
            if args.motions:
                examine_motion_primitives(args.motions)
            else:
                # Find and examine all motion primitive files
                msgpack_files = find_motion_primitive_files()
                if msgpack_files:
                    print("Found motion primitive files:")
                    for file in msgpack_files:
                        examine_motion_primitives(file)
                else:
                    print("No motion primitive files found")

    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
