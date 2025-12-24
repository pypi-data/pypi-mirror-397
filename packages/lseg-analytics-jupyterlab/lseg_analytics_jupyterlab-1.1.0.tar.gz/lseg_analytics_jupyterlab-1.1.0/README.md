# LSEG Extension for JupyterLab

A JupyterLab extension with rich support for the LSEG Analytics Pricing Python SDK (PyPI package: _lseg-analytics-pricing_, hereafter referred to as “the SDK”), providing code automation features such as Intelligent Code Completion and Samples.

- [LSEG Extension for JupyterLab](#lseg-extension-for-jupyterlab)
  - [Introduction](#introduction)
  - [Features Overview](#features-overview)
  - [Usage](#usage)
    - [Commands](#commands)
    - [Coding Assistance](#coding-assistance)
      - [Intelligent Code Completion](#intelligent-code-completion)
      - [Code Samples](#code-samples)
    - [Seamless Authentication](#seamless-authentication)
      - [Seamless Authentication - Implementation](#seamless-authentication---technical-details)
  - [Privacy Statement](#privacy-statement)
  - [License](#license)
  - [Compatibility](#compatibility)
  - [Setup Instructions](#setup-instructions)
  - [Troubleshooting](#troubleshooting)
  - [Questions, issues, feature requests, and contributions](#questions-issues-feature-requests-and-contributions)
  - [Known Issues](#known-issues)

## Introduction

The LSEG JupyterLab Extension is designed to assist coders working on financial applications. It offers a suite of predefined code templates tailored for various financial use cases and intelligent code completion features that help suggest parameter values, ensuring accuracy and efficiency in your financial coding tasks.

The extension provides support for the new LSEG Analytics APIs with coverage for a wide range of asset classes.

## Features Overview

### LSEG Analytics APIs

- **Commands:**
  - Quickly access and execute LSEG Analytics functions from the command palette.
- **Coding Assistance:**
  - **Intelligent Code Completion:**
    - Enjoy real-time, context-aware code completions specifically for LSEG Analytics parameter values, reducing coding errors and boosting productivity.
  - **Code Samples:**
    - Access a library of pre-built code templates for common LSEG Analytics use cases, helping you get started quickly and efficiently.
- **Seamless Authentication:**
  - Easily authenticate to the LSEG Analytics SDK from within JupyterLab, ensuring secure and hassle-free access.

## Usage

### Commands

To use commands, open the Command Palette (Command+Shift+C on macOS and Ctrl+Shift+C on Windows/Linux) and type in one of the following commands:

| Command    | Description |
| -------- | ------- |
| LSEG: Sign in   | Opens window for log in details to start using the extension features.    |
| LSEG: Sign out | Logs user out     |
| LSEG: Refresh Code Completion Data    | Updates the cache of completion data which is used for parameter suggestions.    |

To see all available LSEG Analytics commands, open the Command Palette and type _LSEG:_.

### Coding Assistance

#### Intelligent Code Completion

Dynamic parameter suggestions, based on the data available to the user. To use Intelligent Code Completion:

1.  Place your cursor within a piece of code that requires a parameter.
2.  Trigger the parameter to see a list of possible values using the following method:
    - Type the name of the parameter followed by an equals sign (=) and run the _implicit trigger suggest_ command (`tab`).

##### Tips #####
1. Ensure the same version of the SDK installed in the working environment is installed in the JupyterLab server environment.
2. View method signatures quickly
    - Click on a method name and press `tab` to display its signature, including parameter names.
3. Trigger detailed tooltips
    - Type the method name and insert `(` to prompt a tooltip showing the method definition and docstring. This is especially useful when hover-based tooltips don’t appear reliably. 

#### Code Samples

Samples provide templates of code for key analytics functionality​. To use samples:

1. Select the LSEG icon from the left hand side bar. After logging in, expand **'LSEG Financial Analytics'** tree view and select **'Code Samples'**.
2. Once a compatible version of the SDK is installed in the JupyterLab server environment, expand the sections to browse through the available samples.
3. Open a sample as a notbook or a Python script.
4. Modify it to tailor it to the task you're working on.

Code samples are generated based on the SDK installed in the JupyterLab server environment.
Changing the kernel of a notebook or a Python script will not affect the content displayed on the Code Samples page.

### Seamless Authentication

The LSEG JupyterLab extension (“the extension”) makes it easier to _write_ Python code that uses the _lseg-analytics-pricing_ Python SDK. However, you need to be authenticated to be able to _execute_ your Python code that uses the SDK. 

The SDK provides several authentication mechanisms (see the SDK documentation for more information). One of these is designed to provide a seamless authentication experience when using the extension: if you are logged in to the extension, you do not need to authenticate again to execute your Python code inside JupyterLab. 

By default this is disabled. To enable it, use one of the following methods:

1. Via the extension
  - Open **Settings** directly from the **extension Help** tree view.
  - Select the box **'Enable Automatic Authentication'**.

2. Via the JupyterLab Settings
  - Navigate to **Settings → Settings Editor → LSEG Jupyter Settings**.
  - Check the box labeled **'Enable Automatic Authentication'**.

#### Seamless Authentication - Technical Details

When the setting is enabled, the extension starts a proxy web server that forwards calls from the SDK to the LSEG Financial Analytics backend APIs, adding the necessary authentication token. 

The behaviour of the proxy web server is as follows: 

* The proxy web server runs on http://127.0.0.1, so only the user and scripts/apps running locally can make requests to it. 
* It will only forward SDK requests to the LFA backend; it will not forward requests to unknown endpoints. 
* The extension has an output panel that shows the calls being forwarded to the LFA backend, so it is easy to see all the traffic handled by the proxy. 

There is the possibility that other local scripts/apps could try to access the proxy web server and make requests using it. If this concerns you, you can disable the proxy and use one of the other SDK authentication mechanisms. 

## Privacy Statement
Please read the [Privacy Statement](https://www.lseg.com/en/policies/privacy-statement) governing the use of this extension.

## License
See the LICENSE file installed with the extension.

## Compatibility

- LFA Python SDK Version v1.0+
- JupyterLab web-based IDE Version v4.4.x
- Operating systems: Windows, OS X, Linux

## Setup Instructions

It is strongly recommended to create and activate a dedicated `conda` or `venv` environment prior to launching the JupyterLab Web Application.

All required dependencies should be installed directly from the `Anaconda Powershell Prompt` (or an equivalent terminal outside of JupyterLab) in the JupyterLab server environment.

If installation is performed within the JupyterLab terminal, a session restart may be necessary for the changes to take effect.

### ICC Pre-Requisites

For Intelligent Code Completion (ICC) to work properly, the following tools and plugins need to be installed:
1.	Install the Python backend server that connects Jupyter to language servers via the Language Server Protocol (LSP).
```ini
  pip install jupyter-lsp
```
2.	Install the frontend JupyterLab extension that provides the UI for the LSP features.
```ini
  pip install jupyterlab-lsp
```
3.	Install the below language server for Python:
```ini
pip install python-lsp-server
```
4.	Enable LSP in JupyterLab settings:  
a.	Open JupyterLab.  
b.	Go to the menu bar and select Settings > Settings Editor > Language Servers.  
c.	Activate the Language Server and make sure to include the installed server name in the list.


## Troubleshooting

If you encounter issues while using the extension, you can try the following self-help tips to resolve them.

### Common Actions to Try

- **Log out and log in again:** Sometimes, re-authenticating can resolve issues.
- **Run cache refresh:** Use the `LSEG: Refresh Code Completion Data` command to update the cache of completion data.
- **Restart JupyterLab:** If issues persist, try clearing the LSEG cookies and restart JupyterLab.

### Log Output

Log output will generally come from one of two sources:
1. The extension itself
2. The SDK (`lseg-analytics-pricing`)

The JupyterLab extension adds two output windows: **LSEG Analytics** and **LSEG Analytics - SDK Auth**.

- **LSEG Analytics:** This contains general logging about the behavior of the extension itself, such as logging in, logging out, refreshing data, inserting samples, and providing code completion prompts.
- **LSEG Analytics - SDK Auth:** This contains information about the calls the extension is forwarding to the LFA web backend on behalf of the SDK.

### How to Open the Output Windows

1. Open JupyterLab.
2. Go to the menu bar and select `View → Activate Command Palette` (or press `Ctrl+Shift+C`).
3. In the command palette, use _LSEG: Show Log Console_ command for **LSEG Analytics** logs or _LSEG: Show SDK Auth Log Console_ for **LSEG Analytics - SDK Auth** logs.

### How to Increase the Logging Level
1. Open JupyterLab.
2.	Open the desired log console panel as explained in the previous section (_How to Open the Output Windows_).
3. In the Log Console panel, click on the drop down in front of the **Log Level** setting and select the desired log level from the options: error, warning, info, debug.

### Contact Support

If you need further assistance, please use the following contact information:

- **Help desk Telephone:** +1 888 333 5617
- **MyAccount Portal:** [Product and Content Support | MyAccount](https://myaccount.lseg.com)
  - Select the issue you're having
  - Choose 'LSEG Analytics API' from the dropdown

### Questions, issues, feature requests, and contributions

If you have feedback for the extension please email [analyticschannelsupport@lseg.com](mailto:analyticschannelsupport@lseg.com)

# Release notes
## Version 1.1.0 - December, 2025
- **Bug fixes and minor UI improvements:** Improved ICC for notebooks, standardized prompt UI notifications, and renamed authentication output pane.

## Version 1.0.0 - October, 2025

Version 1.0.0 of the LSEG Financial Analytics (LFA) Extension for JupyterLab. This extension brings dynamic intelligent code completion features tailored specifically for developers working with the LSEG Analytics Pricing Python SDK, empowering them to write code more efficiently and accurately.
