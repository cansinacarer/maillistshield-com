Mail List Shield
================

|Uptime| |Test Coverage| |Last Commit| |Code Style|

Welcome! 👋 You found the documentation for the Flask application served on `maillistshield.com <https://maillistshield.com>`_. Please refer to the `GitHub page of this project <https://github.com/cansinacarer/maillistshield-com>`_ for details about the microservices.

What is Mail List Shield?
-------------------------

Mail List Shield is a SaaS application, designed to help marketers identify and remove invalid emails from their recipient lists to avoid sending to spam traps and improve their email deliverability.

What is Base SaaS Flask?
------------------------

The Flask application is built using my Base SaaS Flask template, which provides base features used by all my SaaS projects built with Flask. You can find the source code for this project on my `GitHub <https://github.com/cansinacarer/My-Base-SaaS-Flask>`_. When I add a major SaaS feature that is not specific to Mail List Shield, I add it to the Base SaaS Flask template then pull it to this project.

You might see the manually written pages of this documentation refer to Base SaaS instead of Mail List Shield. This is because I copied those pages from my Base SaaS. The auto generated documentation however, is built from the docstrings of this project, so it refers to Mail List Shield code specifically.

– `Cansin Acarer <contact.html>`_

.. toctree::
   :maxdepth: 4
   :caption: Documentation:
   
   features
   development
   ci-cd
   deployment
   autoapi/index


.. toctree::
   :maxdepth: 2
   :caption: Additional Resources:
   
   contact




.. |Uptime| image:: https://uptime.apps.cansin.net/api/badge/5/uptime
   :target: https://uptime.apps.cansin.net/status/base-saas-flask-demo
.. |Test Coverage| image:: https://raw.githubusercontent.com/cansinacarer/My-Base-SaaS-Flask/main/tests/coverage/coverage-badge.svg
.. |Last Commit| image:: https://img.shields.io/github/last-commit/cansinacarer/My-Base-SaaS-Flask?color=blue
.. |Code Style| image:: https://img.shields.io/badge/code%20style-black-000000
   :target: https://github.com/psf/black
