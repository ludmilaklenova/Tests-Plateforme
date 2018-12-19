#!/bin/sh
##+=============================================================================
##
## file :         
##
## description :  Ce script met à jour l'infrastructure et lance tous les tests pour le package Device Root Java 
##
##
##-=============================================================================
#

. $PYTESTS_PLATFORM_ROOT/scripts/common_testing_setenv.sh

echo -e "${BLUE}${BOLD}==> Préparation de l'infrastructure ... ${NORMAL}"
$PYTESTS_PLATFORM_ROOT/scripts/drjava_prepare_infra.sh
ret=$?
if [ $ret -ne 0 ]; then
	echo -e "${RED}======== Fatal: Preparation de l'infrastructure Failed. ========${NORMAL}"
	exit 1
fi

echo -e "${BLUE}${BOLD}==> Lancement des tests non fonctionnels, fonctionnel, de fiabilité et de régression ... ${NORMAL}"
$PYTESTS_PLATFORM_ROOT/scripts/drjava_other_tests.sh
ret=$?
if [ $ret -ne 0 ]; then
	echo -e "${RED}======== Fatal: Lancement des tests  Failed. ========${NORMAL}"
	exit 1
fi

echo
echo -e "${GREEN}${BOLD}Execution : " $(basename $0) " done${NORMAL}"

exit 0
 
