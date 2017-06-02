# Synchro Mailchimp
![alt text](https://github.com/sladinji/blousebrothers/blob/master/blousebrothers/confs/management/commands/mailchync.png?raw=true)

**REGLES GENERALES:**

* Tout nouveau statut overwrite le statut précédent
* Tout statut évolue de la manière qui est précisée après le ":"

**REGLES DE REDEMARRAGE DU WORKFLOW (INITIALISATION):**
* - Si pas de wallet: registered
* - Parmi ceux qui ont un wallet: si conf finie à 100% non publiée: creat_conf_100
* - Parmi ceux qui ont un wallet + pas de conf 100% non publiée: si conf en cours de création: creat_conf_begin
* - Parmi ceux qui ont un wallet + pas de conf 100% non publiée + pas de conf en cours de création: si conf publiée: conf_publi_ok
* - Parmi ceux qui ont un wallet + pas de conf 100% non publiée + pas de conf en cours de création + pas de conf publiée: si pas de crédit: wallet_ok
* - Parmi ceux qui ont un wallet + pas de conf 100% non publiée + pas de conf en cours de création + pas de conf publiée + un compte crédité: si pas d'évaluation en attente: money_ok
* - Parmi ceux qui ont un wallet + pas de conf 100% non publiée + pas de conf en cours de création + pas de conf publiée + un compte crédité + une évaluation en attente: give_eval_notok
* tous les autres si il y en a: money_ok

**REGLES D'ATTRIBUTION DES STATUTS SELON L'ACTION:**
* ACTION INSCRIPTION: donne statut "registered": _H24, _J7, _J15, _M1, _inact
* ACTION CREATION WALLET: donne statut "wallet_ok": _H24, _J7, _J15, _M1, _inact
* ACTION CREDIT COMPTE OU ACHAT ABO: donne statut "money_ok": _H24, _J7, _J15, _M1, _inact
* ACTION ACHAT D'UNE CONF: donne statut "buyer_ok": _H24, _J7, _J15, _M1, devient **"money_ok"** à M1+1 jour
* ACTION CONF CONSOMMEE A 100%: donne statut "give_eval_notok": _H24, _J7, _J15, _M1, devient **"money_ok"** à M1+1 jour
* ACTION CONF EVALUEE: donne statut "money_ok": _H24, _J7, _J15, _M1, _inact
* ACTION DEBUT CREATION DE CONF: donne statut "creat_conf_begin": _H24, _J7, _J15, _M1, _inact 
* ACTION CREATION DE CONF 100%: donne statut "creat_conf_100": _H24, _J7, _J15, _M1, _inact
* ACTION CONF PUBLIEE: donne statut "conf_publi_ok": devient **"creat_wait"** à H24
* ACTION CONF VENDUE: donne statut "conf_sold": devient **"creat_wait"** à H24
* ACTION A RECU UNE EVALUATION: donne statut "get_eval_ok", devient **"creat_wait"** à H24
* (ACTION "EST DEVENU STATUT CREAT_WAIT":) creat_wait: devient _H24, _J7, J15, _M1, repasse à J15 à M1+1



**--> RECAPITULATIF DE TOUS LES STATUTS CREES:**

* registered, registered_H24, registered_J7, registered_J15, registered_M1, registered_inact 
*        #envoi de mails incitants à créer son wallet, puis abandon
* wallet_ok, wallet_ok_H24, wallet_ok_J7, wallet_ok_J15, wallet_ok_M1, wallet_ok_inact 
*        #envoi d'emails incitant à acheter un abo ou créditer son compte, puis abandon
* money_ok, money_ok_H24, money_ok_J7, money_ok_J15, money_ok_M1, money_ok_inact 
*        #envoi d'emails incitant à acheter une conf, puis abandon
* buyer_ok, buyer_ok_H24, buyer_ok_J7, buyer_ok_J15, buyer_ok_M1   
*        #envoi d'emails incitants à terminer son dossier (puis retour à l'incitation d'achat en devenant money_ok)
* give_eval_notok, give_eval_notok_H24, give_eval_notok_J7, give_eval_notok_J15, give_eval_notok_M1  
*        #envoi d'emails incitants à évaluer le dossier (puis retour à l'incitation d'achat en devenant money_ok)
* creat_conf_begin, creat_conf_begin_H24, creat_conf_begin_J7, creat_conf_begin_J15, creat_conf_begin_M1, creat_conf_begin_inact 
*        #envoi d'emails incitant à terminer la rédaction, puis abandon
* creat_conf_100, creat_conf_100_H24, creat_conf_100_J7, creat_conf_100_J15, creat_conf_100_M1, creat_conf_100_inact 
*        #envoi d'emails incitant à publier, puis abandon
* conf_publi_ok:
*        #félicitation (une seule fois) , puis retour à l'incitation en devenant creat_wait
* conf_sold 
*        #envoi email de féicitations (une seule fois)
* get_eval_ok 
*        #envoi email d'info (une seule fois)
* creat_wait, creat_wait_H24, creat_wait_J7, creat_wait_J15, creat_wait_M1, boucle sur creat_wait_J15... etc
*        #incite à créer d'autres dossiers


**--> EMAILS ACTIONS:**

Merge tag à updater: action (MMERGE28)
Change to publi: envoi l'email de confirmation de publication de conf
Change to credit: envoi l'email de confirmation de crédit de compte
Change to abo: envoi email confirmation abonnement
Change to virement: envoi email confirmation virement
Change to welcome: envoi email de bienvenue à l'inscription
Change to credit_low: envoi email incitation à créditer le compte

