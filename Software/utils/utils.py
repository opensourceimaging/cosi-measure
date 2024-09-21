from datetime import datetime
import subprocess


def get_formatted_datetime():
    # Get current date and time
    now = datetime.now()
    # Format it as yyyy-mm-dd-hh-mm
    formatted_datetime = now.strftime('%Y-%m-%d-%H-%M')
    return formatted_datetime


def run_bash_script(script_path):
    # Store the output for later return
    output = []
    
    # Open a subprocess to run the bash script
    process = subprocess.Popen(['bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Stream output live
    while True:
        # Read a line from stdout
        output_line = process.stdout.readline()
        
        # If the output is empty and process finished, break
        if output_line == '' and process.poll() is not None:
            break
        
        # If there's output, print it and save to the list
        if output_line:
            print(output_line, end='')  # Live output
            output.append(output_line)
    
    # Wait for the process to complete
    process.wait()
    
    # Collect any remaining stderr and include it in the output
    stderr_output = process.stderr.read()
    if stderr_output:
        output.append(stderr_output)
        print(stderr_output, end='')
    
    # Join the output into a single string and return it
    return ''.join(output)



def run_bash_command(command):
    # Store the output for later return
    output = []
    
    # Open a subprocess to run the bash command
    process = subprocess.Popen(['bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Stream output live
    while True:
        # Read a line from stdout
        output_line = process.stdout.readline()
        
        # If the output is empty and process finished, break
        if output_line == '' and process.poll() is not None:
            break
        
        # If there's output, print it and save to the list
        if output_line:
            print(output_line, end='')  # Live output
            output.append(output_line)
    
    # Wait for the process to complete
    process.wait()
    
    # Collect any remaining stderr and include it in the output
    stderr_output = process.stderr.read()
    if stderr_output:
        output.append(stderr_output)
        print(stderr_output, end='')
    
    # Join the output into a single string and return it
    return ''.join(output)