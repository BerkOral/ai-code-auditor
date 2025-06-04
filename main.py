import os
from rich.console import Console
from dotenv import load_dotenv
from analyzer.dispatcher import dispatch_analysis

# Load environment variables
load_dotenv()
console = Console()

def main():
    console.print("[bold green]🚀 AI Code Security Auditor Starting...[/]")
    file_path = input("Enter here for scan: ")
    
    if not os.path.isfile(file_path):
        console.print(f"[red]❌ Error: File not found at {file_path}[/]")
        return

    dispatch_analysis(file_path)

if __name__ == "__main__":
    main()
