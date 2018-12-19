#!/bin/sh
#
#	This scripts aims at testing the dependency of CPP package regarding .so files
#

#-------------------------------------------------------------------------------
#
# Manage input arguments
#
#-------------------------------------------------------------------------------
# init vars
d_is_set=
s_is_set=
l_is_set=

# help
usage() {
	echo
	echo "  Usage: $(basename $0) OPTIONS"
	echo
	echo "      -d absolute path of CPP "
	echo "      -s absolute path of scan plugin"
	echo "      -l absolute path of log files"
	echo
	echo "      [-h] print this help and exit"
	echo 
	exit 2
}

# get options
while getopts "d:s:l:h" opt; do
  #echo DEBUG: found option: $opt $OPTIND $OPTARG

  if [ ! -z $(echo "$OPTARG" | grep \^-) ]; then
		echo "Option -$opt requires an argument." >&2
		exit 1
  fi

  case $opt in
    d)
	  d_is_set=1
	  DEVICEROOTPATH=$OPTARG
      ;;
    s)
	  s_is_set=1
	  SCANPLUGINROOTPATH=$OPTARG
      ;;
    l)
	  l_is_set=1
	  LOGFILEPATH=$OPTARG
      ;;
    h)
	  usage
      ;;
    \?)
      echo "Invalid option: -$OPTARG (use -h for help)" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument (use -h for help)." >&2
      exit 1
      ;;
  esac
done

#remove logfile
[ -e $LOGFILEPATH ] && /bin/rm $LOGFILEPATH

# check options and parameters

if [ ! $d_is_set ] || [ ! $s_is_set ] || [ ! $l_is_set ]; then
	echo "Options -d -s and -l are mandatory (use -h for help)."
	exit 1
fi

echo "DEVICEROOTPATH ="$DEVICEROOTPATH >> $LOGFILEPATH
echo "SCANPLUGINROOTPATH ="$SCANPLUGINROOTPATH >> $LOGFILEPATH
echo "LOGFILEPATH = "$LOGFILEPATH >> $LOGFILEPATH

#-------------------------------------------------------------------------------
#
#    Setting environnement variables
#
#-------------------------------------------------------------------------------
echo "Setting environnement variables"

export LD_LIBRARY_PATH=$DEVICEROOTPATH/lib
if [ ! -d "$LD_LIBRARY_PATH" ]; then
    echo "LD_LIBRARY_PATH directory doesn't exist"
    exit 1
fi

#
# these environnement variables must be set before testing package 
#
#if [ -z "$LD_LIBRARY_PATH" ]; then
#    echo "Need to set LD_LIBRARY_PATH"
#    exit 1
#fi

# Now check all dynamic libraries are found in the Deviceroot package 
#
text="\nNow checking if all dynamic libraries are found in the Deviceroot package\n "
echo -e $text

result_deviceroot=`for j in $(find $DEVICEROOTPATH/ -type f -name '*'); do v=$(ldd $j | grep -i found); test -n "${v}" && echo -e "\n Binary file= ${j}:\n ${v}" ;done `
check_result_deviceroot=`echo $result_deviceroot|grep found`

# now put result in log file
echo "Tests Dependency results for DeviceRoot" >> $LOGFILEPATH
echo -e $text >> $LOGFILEPATH
echo "$result_deviceroot" >> $LOGFILEPATH

#
# Now check if a binary is not linked with 2 versions of the same libraries in the Deviceroot package 
#
text="Tests if a binary of the Deviceroot package is not linked with multiples versions of the same libraries \n "
echo -e $text
echo -e $text >> $LOGFILEPATH

multiples_versions_deviceroot_libs=`for j in $(find $DEVICEROOTPATH/ -type f -name '*'); do v=$(ldd $j |awk '{print $1}'|awk -F"-" '{print $1}'|awk -F"." '{print $1}'|sort |uniq -d ) ; test -n "${v}" && echo -e "\n Binary file= ${j}  is linked with multiples versions of the same libraries  :\n ${v}" ;done`
echo "$multiples_versions_deviceroot_libs" >> $LOGFILEPATH

# Now check if the Deviceroot package is not contain doubles of the same libraries 
#
text="Tests if the Deviceroot package does not contain double libraries \n "
echo -e $text 
echo -e $text >> $LOGFILEPATH  

same_libraries_deviceroot=`find $DEVICEROOTPATH/lib/ -maxdepth 1 -type f -name '*.so' |awk '{print $1}'|awk -F"-" '{print $1}'|awk -F"." '{print $1}' | sort| uniq -d`

#check operation result
check_same_libraries_deviceroot=`v=$(echo $same_libraries_deviceroot); test -n "${v}" && echo -e "\n Deviceroot package contain doubles of the same libraries:\n ${v}"`
echo "$check_same_libraries_deviceroot" >> $LOGFILEPATH

#
# Now check all dynamic libraries are found in the ScanPlugin package 
#
text="Now checking if all dynamic libraries are found in the ScanPlugin package\n "
echo -e $text
echo -e $text >> $LOGFILEPATH
result_scanplugin=`for j in $(find $SCANPLUGINROOTPATH/ -type f); do v=$(ldd $j | grep -i found); test -n "${v}" && echo -e "\n Plugin file= ${j}:\n ${v}" ;done` 
check_result_scanplugin=`echo $result_scanplugin|grep found`

# now put result in log file
echo "$result_scanplugin" >> $LOGFILEPATH

#
# Now check if a binary is not linked with 2 versions of the same libraries in the ScanPlugin package 
#
text="Tests if  a binary of the ScanPlugin package is not linked with multiples versions of the same libraries "
echo -e $text
echo -e $text >> $LOGFILEPATH

multiples_versions_scanplugin_libs=`for j in $(find $SCANPLUGINROOTPATH/ -type f -name '*'); do v=$(ldd $j |awk '{print $1}'|awk -F"-" '{print $1}'|awk -F"." '{print $1}'|sort |uniq -d ) ; test -n "${v}" && echo -e "\n Plugin file= ${j}  is linked with multiples versions of the same libraries  :\n ${v}" ;done`

echo "$multiples_versions_scanplugin_libs" >> $LOGFILEPATH
#
#  Now check tests results
#
if [[ -z $check_result_deviceroot ]] && [[ -z $check_result_scanplugin ]] && [[ -z $same_libraries_deviceroot ]] && [[ -z $multiples_versions_deviceroot_libs ]] && [[ -z $multiples_versions_scanplugin_libs ]]; then
text="\nPackage DeviceRoot-CPP is consistent"
echo -e $text
echo -e $text >> $LOGFILEPATH;
echo "Please look at log files  " $LOGFILEPATH ;
echo "return code 0" >> $LOGFILEPATH;
exit 0; 
fi

# exit with error
text="\nPackage CPP is not consistent"
echo -e $text
echo -e $text >> $LOGFILEPATH
echo "Please look at log files " $LOGFILEPATH
echo "return code 1" >> $LOGFILEPATH
exit 1
