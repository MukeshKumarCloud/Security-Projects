import tkinter as tk
import subprocess

def scan_network():
    ip_address = entry_ip.get()
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Scanning network: {ip_address}\n\n")

    try:
        output = subprocess.check_output(["nmap", "-F", ip_address])
        result_text.insert(tk.END, output.decode("utf-8"))
    except subprocess.CalledProcessError:
        result_text.insert(tk.END, "An error occurred while scanning the network.")

window = tk.Tk()
window.title("Network Scanner")

label_ip = tk.Label(window, text="Enter IP Address:")
label_ip.pack()
entry_ip = tk.Entry(window)
entry_ip.pack()
scan_button = tk.Button(window, text="Scan Network", command=scan_network)
scan_button.pack()

result_text = tk.Text(window)
result_text.pack()

window.mainloop()
