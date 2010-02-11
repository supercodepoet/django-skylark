#!/bin/bash
DOJORELEASEVERSION="1.4.1"
DOJORELEASEBASENAME="dojo-release-$DOJORELEASEVERSION-src"
DOJORELEASEFILE="dojo-release-$DOJORELEASEVERSION-src.tar.gz"
DOJODIR="$DOJORELEASEBASENAME"
PROFILE="ribt_dojo.profile.js"
DESTDIR="../crunchyfrog/templates/ribt/media/_build"
BUILDDIR="$DOJODIR/util/buildscripts"
BUILD="build.sh"

if [ ! -f "./$DOJORELEASEFILE" ]; then
    curl -O http://download.dojotoolkit.org/release-$DOJORELEASEVERSION/$DOJORELEASEFILE
fi

if [ ! -d "./$DOJODIR" ]; then
    tar -xvzf dojo-release*.tar.gz
fi

if [ -f "$BUILDDIR/$BUILD" ]; then
    cd $BUILDDIR
    ./$BUILD action=clean,release dojodir=../../../$DOJODIR profileFile=../../../$PROFILE releaseDir=../../../$DESTDIR version=$DOJORELEASEVERSION optimize=none copyTests=false
    cd ../../../$DESTDIR/dojo
    # And we don't need the dojox directory, so trash it
    rm -rf dojox
    rm -rf ../../dojo
    mv dojo ../../
    cd ../../
    rm -rf _build
fi
