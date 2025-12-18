# Github Copilot

If you are used to working with AI tools like Amazon Q, Cursor, etc., you need to understand how GitHub Copilot differs in behavior.

__**COPILOT DOES NOT AUTOMATICALLY READ CONTEXT FILES!**__

GitHub Copilot does not automatically read or understand the context files in your repository. 

It generates code based on the immediate context of the file you are editing and any comments or code snippets you provide. 

To get the best results, you need to explicitly provide context through comments or code snippets.


## Starting a new conversation

When starting a new conversation with Copilot, **ASK COPILOT TO READ [APPLICATION_CONTEXT.md](APPLICATION_CONTEXT.md) AND USE IT AS CONTEXT.** 

you should provide context about what you want to achieve. 

This can be done by adding comments or code snippets that describe the desired functionality.

This application has an APPLICATION_CONTEXT.md file that provides an overview of the application's purpose, architecture, and key components. It also contains references to important rules and standards that must be followed.

