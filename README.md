# Intro

The following are start to finish instructions to setting up the internet in a box. First we must setup the hardware, then the Pi software, then the application software, which varies by network.

## Hardware Setup
1. Connect the power adapters for the 'Arduino', 'Switch', and 'LAN I'. LAN E and LAN T do not work at time of writing.
2. Press the button next to the top, leftmost Raspberry Pi, the pi marked 'R'. The LED next to this Rasp Pi should now be the only one illuminated.
3. Connect the USB lead to your computer.

###Windows

4. Open device manager and find which COM port is in use (COM1-4)
5. Open the PuTTY application (download it if not installed).
6. In PuTTY, select 'Serial', set the 'Serial line' to COM1-4, as found in step 3, and set the baud rate to 155200. Click open to start the serial session.
7. Press enter once to get the login prompt from the Raspberry Pi

###Linux:

4. Open terminal.
5. Run `finddev`. It may fail. If it fails, run `curl https://raw.githubusercontent.com/ManickYoj/CN-Internet/master/Scripts/finddev.bash >> ~/.bashrc && source ~/.bashrc ` to install the `finddev` script. Then run `finddev`
6. One of the results should be of the format `/dev/ttyUSB0 - Prolific_Technology_Inc._USB-Serial_Controller`. The `/dev/ttyUSB0` segment of the line is the port you'll need for the serial connection.
7. Run `picocom /dev/ttyUSB0 -b 115200` with the port found in step 5 to start the serial session. If picocom is not installed, run `sudo apt-get install picocom`, the run `picocom /dev/ttyUSB0 -b 115200`.
8. Press enter once to get the login prompt from the Raspberry Pi

## Software Setup
To setup the software. We must connect to Raspberry Pis in sequence and start their respective software. Every pi uses the username: 'pi', password: 'raspberry'.

### Network 'I'
The router ('R') must be set up first, the other two raspberry Pis can be setup in any order.


####Pi R:
Once logged in, run the following command:

- `sudo python3 Desktop/CN-Internet/morrowrouter.py` will start the router. It will take a second to start, and will display some confirmation when complete.

####Pi I (IP 0.0.73.73) & N (IP 0.0.73.78):
Once logged in, run the following commands:

- `cd Desktop/CN-Internet`
- `sudo python3 moros.py` will start the pseudo-OS for applications. It will take a second to start, and will display some confirmation when complete.
- Within morOS, use the first pi (I or N) to run the chatserver application with `run chatserver`. Use the second pi (I or N) to run the chatclient application with `run chatclient`. Use `help` in morOS if confused, or `.help` in either chatserver or chatclient if confused.
    - Within the chatclient application, you will need to set the destination IP of the messages sent by the application. If the chatclient is attempting to communicate with a server on pi 'I', use command `.setDestIP 0.0.73.73`. Otherwise, to communicate with pi 'N', use command `.setDestIP 0.0.73.78`. Use `.help` if confused.

You should now be able to send messages from the chat client to the chat server. The server will repeat these messages out to any other connected clients, and log them. If you connect to the server pi, you can show these messages with the `.showLog` command.

That's it for now. Please contact Nick Francisci (nickfrancisci@gmail.com) for additional help.
