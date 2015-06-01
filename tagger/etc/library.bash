loadup() {

  if [ -n "${features}" ]; then
    if [ -z "${tmp}" ]; then tmp="${LOGONTMP}/.logon.${USER}.io.$$"; fi
    echo "${features}" | sed -e 's/^,//' -e 's/,/\n/g' > ${tmp};
    while read i; do 
      echo "(pushnew :${i} *features*)";
    done < ${tmp};
    /bin/rm -f ${tmp};
  fi
  
  #
  # when running from source, configure and compile the LOGON system
  #
  if [ -n "${source}" ]; then
    echo "(pushnew :logon *features*)";
    echo "(load \"${LOGONROOT}/lingo/lkb/src/general/loadup.lisp\")";
    echo "(pushnew :lkb *features*)";
    echo "(compile-system \"tsdb\")";
  fi

  if [ -n "${prologue}" -a -f "${prologue}" ]; then
    echo "(load \"${prologue}\")";
  fi

} # loadup

gc() {

  echo "(setf tsdb::*tsdb-gc-verbosity* '(:stats))";
  echo "(setf tsdb::*tsdb-gc-debug*
          (cons
           '((1 :new :zoom) (5 :old :room))
           '((1 :new :old :holes :room))))";

} # gc()


reset() {

  ( cd ${LOGONROOT}; make reset; )

} # reset()


pure() {

  ( cd ${LOGONROOT}; make pure; )

} # pure()


epilogue() {

  if [ -n "${epilogue}" -a -f "${epilogue}" ]; then
    echo "(load \"${epilogue}\")";
  fi

} # epilogue()


#
# first, work out the current operating system, one of `linux' (x86), `solaris'
# (sparc), or `windows' (x86); anything else will require manual installation.
#
if [ -z "${LOGONOS}" ]; then
  if [ "$OSTYPE" = "linux" -o "$OSTYPE" = "linux-gnu" ]; then
    #
    # apparently, (some) Debian installations come with an older uname(1), 
    # where `-i' is not available :-{.                          (11-mar-05; oe)
    #
    if uname -i > /dev/null 2>&1; then
      cpu=$(uname -i)
      if [ "${cpu}" = "unknown" ]; then cpu=$(uname -m); fi
    else
      cpu=$(uname -m)
    fi
    case "${cpu}" in
      i?86)
        LOGONOS="linux.x86.32"
        ;;
      x86_64)
        LOGONOS="linux.x86.64"
        ;;
      *)
        echo "LOGONOS: unknown Linux variant (check \`uname -m'); exit."
        exit 1;
    esac
  elif [ "$OSTYPE" = "solaris" -o "${OSTYPE%%?.?}" = "solaris" ]; then
    LOGONOS="solaris";
  elif [ "$OSTYPE" = "cygwin" ]; then
    LOGONOS="windows";
  fi
fi
export LOGONOS

#
# even on systems that have no Motif installed, make sure the LKB can find its
# Motif libraries (this is somewhat of a hack, really).
#
if [ "$OSTYPE" = "linux" -o "$OSTYPE" = "linux-gnu" ]; then
  if [ -z "${LD_LIBRARY_PATH}" ]; then
    LD_LIBRARY_PATH=${LOGONROOT}/lingo/lkb/lib/${LOGONOS}
  else
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${LOGONROOT}/lingo/lkb/lib/${LOGONOS}
  fi
  export LD_LIBRARY_PATH
  #
  # on 64-bit machines, also include 32-bit libraries, so we can run things in
  # compatibility mode.
  #
  if [ "${LOGONOS}" = "linux.x86.64" ]; then
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${LOGONROOT}/lingo/lkb/lib/linux.x86.32
  fi
fi
