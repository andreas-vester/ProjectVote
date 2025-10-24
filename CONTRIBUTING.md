# Contributing to ProjectVote

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved. The community looks forward to your contributions. 🎉

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
> - Star the project
> - Tweet about it
> - Refer this project in your project's README
> - Mention the project at local meetups and tell your friends/colleagues

## Table of Contents

- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
- [Improving The Documentation](#improving-the-documentation)
- [Style guides](#style-guides)
  - [Code formatting](#code-formatting)
  - [Linting](#linting)
  - [Commit Messages](#commit-messages)
- [Attribution](#attribution)

## I Have a Question

> If you want to ask a question, we assume that you have read the available [Documentation](README.md).

Before you ask a question, it is best to search for existing [issues](https://github.com/andreas-vester/ProjectVote/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue.

If you then still feel the need to ask a question and need clarification, we recommend the following:
- Open a new [issue](https://github.com/andreas-vester/ProjectVote/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (Python version etc.), depending on what seems relevant.
- Attach the "question" label to your newly created issue.

We will then take care of the issue as soon as possible.

## I Want To Contribute

> ### Legal Notice
> When contributing to this project, you must agree that you have authored 100% of
> the content, that you have the necessary rights to the content and that the content
> you contribute may be provided under the project license.

### Reporting Bugs

#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment components/versions (Make sure that you have read the [documentation](README.md). If you are looking for support, you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/andreas-vester/ProjectVote/issues?q=label%3Abug).
- Collect information about the bug:
  - Stack trace (Traceback).
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM).
  - Version of the interpreter, compiler, SDK, runtime environment, package manager, depending on what seems relevant.
  - Possibly your input and the output.
  - Can you reliably reproduce the issue? And can you also reproduce it with older versions?

#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including
> sensitive information to the issue tracker, or elsewhere in public. Instead,
> sensitive bugs must be sent by email to <andreas@vester-online.de>.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:
- Open an [issue](https://github.com/andreas-vester/ProjectVote/issues/new). (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed:
- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there are no reproduction steps or no obvious way to reproduce the issue, the team will ask you for those steps and mark the issue as `needs-repro`. Bugs with the `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be marked `needs-fix`, as well as possibly other tags (such as `critical`), and the issue will be left to be [implemented by someone](#your-first-code-contribution).

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for **ProjectVote**, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation](README.md) carefully and find out if the functionality is already covered.
- Perform a [search](https://github.com/andreas-vester/ProjectVote/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature.

#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/andreas-vester/ProjectVote/issues).
- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Use **feat:** as a prefix, e.g. "feat: Add awesome enhancement".
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- You may want to **include screenshots and animated GIFs** which help you demonstrate the steps or point out the part which the suggestion is related to.
- **Explain why this enhancement would be useful** to most **ProjectVote** users. You may also want to point out other projects that solved it better and which could serve as inspiration.

### Your First Code Contribution

You can find a good [introduction](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) on how to contribute to an open source project. In a nutshell, the process involves the following steps:

1. Fork (i.e. copy) the repository to your own GitHub account.
2. Clone the fork to your local machine.
3. Create a new branch to work on.
4. Commit and push your changes to your own GitHub.
5. Create the Pull Request.

#### How do I set up my dev environment?

**ProjectVote** uses [uv](https://docs.astral.sh/uv/) to manage its dependencies. So make sure you have it properly installed before you go on.

To set up your development environment, you should create a virtual environment and install the project's dependencies:
```shell
uv sync
```

#### Further dev setup and what I need to now about "pre-commit"

Before you commit your code changes, you should make sure, that you only commit code that is of good quality and adheres to the projects [Style guides](#style-guides).

`pre-commit` hooks run all the auto-formatters, linters, and other quality checks to make sure the changeset is in good shape before a commit/push happens. If it finds any issues with your code, `pre-commit` will prevent the actual commit. You then have the chance to fix all issues and re-commit your code changes.

You can install the hooks with (runs for each commit):
```shell
pre-commit install
```

Or if you want them to run only for each push:
```shell
pre-commit install -t pre-push
```

Or if you want to run all checks manually for all files:
```shell
pre-commit run --all-files
```

#### How do I execute unit tests?

Running simple unit tests using `pytest` is as easy as
```shell
uv run pytest
```

### Improving The Documentation

The documentation is written in _Markdown_. If you feel something isn't as clear described as it should be, please don't hesitate to open an [issue](https://github.com/andreas-vester/ProjectVote/issues/new). Also, please attach the **documentation** label to it in order to make the maintainers' life a bit easier.

## Style guides

### Code formatting and linting

We use [ruff](https://pypi.org/project/ruff/) as our tool of choice for style guide enforcement.

### Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. This will help us to automatically generate the changelog.

## Attribution

This guide is based on the **contributing-gen**. [Make your own](https://github.com/bttger/contributing-gen)!
