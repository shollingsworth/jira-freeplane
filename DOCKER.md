# JIRA Freeplane issue creator

## Software Requirements

- [Freeplane](http://freeplane.sourceforge.net/)
- Pick one
    - [Python](http://www.python.org/)
    - [Docker](https://www.docker.com/)

## Installation

### Python

``` bash
pip install jira_freeplane
```

### Docker - [jira-freeplane](https://hub.docker.com/r/hollingsworthsteven/jira-freeplane/)

``` bash
docker pull hollingsworthsteven/jira-freeplane
```

## Quickstart

-   Create a new mindmap, see [sample.mm](https://github.com/shollingsworth/jira-freeplane/blob/main/examples/sample.mm) as an example.

### docker (interactive mode)

> This assumes you are running bash or zsh as your shell
> 
> Replace `$mindmap` with the file name / path of your mindmap.
> 
> Replace `$JIRA_USER`, and `$JIRA_PASS` with your JIRA credentials.
> 
> (You can also use environment variables if you do not want them to show
> in your command history)
> 
> do not change `/config/freeplane_doc.mm` only `$mindmap`

``` bash
docker run --rm -it -v "$(pwd):/app" -v "$mindmap:/config/freeplane_doc.mm" -e "JIRA_USER=${JIRA_USER}" -e "JIRA_PASS=${JIRA_PASS}" -u "$(id -u):$(id -g)" hollingsworthsteven/jira-freeplane jira-freeplane --interactive /config/freeplane_doc.mm
```

### python/pip

> replace
>
> `<your_jira_username>`
>
> and
>
> `<your_jira_password>`
>
> with your JIRA credentials.

``` bash
pip install jira_freeplane
export JIRA_USER=<your_jira_username>
export JIRA_PASS=<your_jira_password>
jira-freeplane -i /path/to/mindmap.mm
```

## Contribute

Pull requests are welcome!

-   [Issue Tracker](https://github.com/shollingsworth/jira-freeplane/issues)
-   [Source Code](github.com/shollingsworth/jira-freeplane)

## Support

Unfortunately, there is no support for this project. We do welcome contributions and pull requests though!

## License

The project is licensed under the MIT license. see [LICENSE](https://github.com/shollingsworth/jira-freeplane/blob/main/LICENSE.txt)
