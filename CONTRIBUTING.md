# Contributing
We welcome contributions of all types including:
* Proposing new features
* Reporting a bug
* Fixing a bug
* Enhancing documentation
* Materials describing the usage of KubeLibrary that we could link from this repository

## Reporting issues
We use [GitHub issues](https://github.com/devopsspiral/KubeLibrary/issues) for reporting bugs, feature proposals and discussions.
When reporting a bug, please include following information:

* Summary of the problem and context
* Steps to reproduce. We are mostly using k3s/k3d and kind as a test clusters, if you could reproduce your problem there that 
would be easier for others to follow. Attach logs, files and anything that was used and might be helpful in investigation.
* What you expected
* What actually happened
* Comments, including your understanding of a problem, possible fix, etc.

## Pull Request checklist
* Create an issue first if you expect the topic needs some more discussion.
* Provide meaningful subject of a PR so that it could become commit message.
* Provide good description, context and link to issues which are resolved.
* Create examples of new funtionality. We keep them in testcases/ dir, and they are all executed as a part of CI. 
This is part of our documentation and verification. We encourage you to use existing test setup (helm deployed services) but suggestions for
change or adding new ones are ok.
* It would be perfect to write unit tests for what you are adding. It is not always needed for simple k8s object getters, but are mandatory
 for more complex logic.
