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
                .on( 'click', async function () {
                    console.log( 'ping' );
                    const userName = $this.text();
                    let oldClipText = '';
                    try {
                        oldClipText = await navigator.clipboard.readText();
                        console.log('read from clipboard', oldClipText);
                    } catch (error) {
                        console.log('Failed to read from clipboard', error);
                        return;
                    }
                    const match = oldClipText.match(/^{{ping|(?<oldUserNames>[^}]*)}}$/);
                    let newClipText = '';
                    if (match) {
                        newClipText = '{{ping|' + match.groups.oldUserNames + '|' + userName + '}}';
                    }
                    else {
                        newClipText = '{{ping|' + userName + '}}';
                    }

                    try {
                        await navigator.clipboard.writeText('{{ping|' + $this.text() + '}}');
                        console.log('copied to clipboard');
                    } catch (error) {
                        console.log('Failed to copy!', error);
                        return;
                    }
                });
        $button.insertAfter( $this );
    } );
});
