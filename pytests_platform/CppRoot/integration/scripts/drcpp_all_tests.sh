#!/bin/sh
##+=============================================================================
##
## file :         
##
## description :  Ce script met à jour l'infrastructure et lance tous les tests pour le package 
##
##
##-=============================================================================
#

. $PYTESTS_PLATFORM_ROOT/scripts/common_testing_setenv.sh

# Tests de déploiement
echo -e "${BLUE}${BOLD}==> Tests de déploiement ... ${NORMAL}"
$PYTESTS_PLATFORM_ROOT/scripts/dr_deployment_tests.sh
ret=$?
if [ $ret -ne 0 ]; then
	echo -e "${RED}======== Fatal: Test de déploiement Failed. ========${NORMAL}"
	exit 1
fi

echo -e "${BLUE}${BOLD}==> Préparation de l'infrastructure ... ${NORMAL}"
$PYTESTS_PLATFORM_ROOT/scripts/dr_prepare_infra.sh
ret=$?
if [ $ret -ne 0 ]; then
	echo -e "${RED}======== Fatal: Preparation de l'infrastructure Failed. ========${NORMAL}"
	exit 1
fi

echo -e "${BLUE}${BOLD}==> Lancement des tests non fonctionnels, fonctionnel, de fiabilité et de régression ... ${NORMAL}"
$PYTESTS_PLATFORM_ROOT/scripts/dr_other_tests.sh
ret=$?
if [ $ret -ne 0 ]; then
	echo -e "${RED}======== Fatal: Lancement des tests  Failed. ========${NORMAL}"
	exit 1
fi

echo
echo -e "${GREEN}${BOLD}Execution : " $(basename $0) " done${NORMAL}"

exit 0
 
