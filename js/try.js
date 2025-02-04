 "use strict";
 
// import { cdxIconBellOutline } from '@wikimedia/codex-icons';

mw.hook('wikipage.content').add(function ( $content ) {
    console.log('try.js loaded');
    // If the content is not a valid jQuery object, we can't do anything.
    if ( !$content.jquery ) {
        console.log('not a valid jQuery object');
        return;
    }
    const pageName = mw.config.get( 'wgPageName' );
    const dykNomPattern = new RegExp('^Template:Did_you_know_nominations/');
    if (!dykNomPattern.test(pageName)) {
      return;
    }
    const userSubpagePattern = new RegExp('^/wiki/User:[^/]+$');
    const $users = $content.find( 'a' )
        .filter(function (index) {
            return userSubpagePattern.test($(this).attr('href'));
        });
    console.log( $content );
    console.log( $users );

    $users.each(function () {
        const $this = $( this );
        const $button = $( '<button>' )
                .text( 'ping' )
                .on( 'click', function () {
                    console.log( 'ping' );
                    $this.text( '@' + $this.text() );
                } );
        $button.insertAfter( $this );
    } );
});
