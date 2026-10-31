![Banner](banner.png)

# codeintel-Code-Duplication-Detector
Identifies and reports instances of duplicated code blocks within a codebase to improve maintainability and reduce potential bugs. If any Python file under the target cannot be read, the report still covers the files that were read, names the unreadable files in the log and in the report, does not print the clean no duplicates line for that run, and the run exits 1. - Focused on Tools for static code analysis, vulnerability scanning, and code quality assurance

## Install
`git clone https://github.com/ShadowStrikeHQ/codeintel-code-duplication-detector`

## Usage
`./codeintel-code-duplication-detector [params]`

## Parameters
- `-h`: Show help message and exit
- `-m`: Minimum number of lines for a code block to be considered a duplicate.
- `-r`: Path to the report file.
- `-e`: List of file or directory names to exclude from the analysis.

## License
Copyright (c) ShadowStrikeHQ
