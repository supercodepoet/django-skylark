#!/bin/bash
DOJORELEASEVERSION="1.5.0"
DOJORELEASEBASENAME="dojo-release-$DOJORELEASEVERSION-src"
DOJORELEASEFILE="dojo-release-$DOJORELEASEVERSION-src.tar.gz"
DOJODIR="$DOJORELEASEBASENAME"
PROFILE="chirp_dojo.profile.js"
DESTDIR="../src/skylark/templates/chirp/media/_build"
BUILDDIR="$DOJODIR/util/buildscripts"
BUILD="build.sh"

if [ ! -f "./$DOJORELEASEFILE" ]; then
    curl -O http://download.dojotoolkit.org/release-$DOJORELEASEVERSION/dojo-release-$DOJORELEASEVERSION-src.tar.gz
fi

if [ ! -d "./$DOJODIR" ]; then
    tar -xvzf dojo-release*.tar.gz
fi

if [ -f "$BUILDDIR/$BUILD" ]; then
    cd $BUILDDIR
    ./$BUILD action=clean,release dojodir=../../../$DOJODIR profileFile=../../../$PROFILE releaseDir=../../../$DESTDIR version=$DOJORELEASEVERSION optimize=none copyTests=true
    cd ../../../$DESTDIR/dojo
    pwd
    rm -rf ../../dojo
    rm -rf ../../dojox
    mv dojo ../../
    mv dojox ../../
    cd ../../
    pwd
    rm -rf _build
fi
