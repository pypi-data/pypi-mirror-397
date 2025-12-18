###############################
 Res Partner API - SomConnexio
###############################

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
   :alt: Beta
   :target: https://odoo-community.org/page/development-status

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :alt: License: AGPL-3
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html

.. |badge3| image:: https://img.shields.io/badge/gitlab-coopdevs%2Fodoo--somconnexio-lightgray.png?logo=gitlab
   :alt: coopdevs/som-connexio/odoo-somconnexio
   :target: https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio

|badge1| |badge2| |badge3|

This module is a part of SomConnexió original module.

We are working to separate the monolitic original module in small
modules splited by functionalities.

This module manage the integration between Odoo and a external
application using an API.

Res Partner API module centralize all the operations involving
`res.partner` model. Alone or through `contract.contract`.

**Table of contents**

.. contents::
   :local:

**************
 Contributors
**************

-  ``Som Connexió SCCL <https://somconnexio.coop/>``

   -  Gerard Funonsas gerard.funosas@somconnexio.coop
   -  Borja Gimeno borja.gimeno@somconnexio.coop

-  ``Coopdevs Treball SCCL <https://coopdevs.coop/>``

   -  Daniel Palomar daniel.palomar@coopdevs.org
   -  César López cesar.lopez@coopdevs.org

*******
 Usage
*******

This module provides a REST API to manage partner-related operations in
Odoo. Below are the key endpoints and their functionalities:

-  **Get Partner**: - Endpoint: `/api/partner/get` - Method: GET -
   Description: Retrieve details of an existing partner by REF.

-  **Search Partner by VAT**: - Endpoint: `/api/partner/search` -
   Method: GET - Description: Retrieve details of an existing partner
   searching it by their VAT number.

-  **Change Partner Email**: - Endpoint:
   `/api/partner-email-change/create` - Method: POST - Description:
   Change the email of an existing partner using the email change
   wizard.
