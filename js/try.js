mw.hook('wikipage.content').add(function ( $content ) {
    console.log('try.js loaded');
    // If the content is not a valid jQuery object, we can't do anything.
    if ( !$content.jquery ) {
        console.log('not a valid jQuery object');
        return;
    }
    const $users = $content.find( "a.userlink[href ^= '/wiki/User:']" );
    console.log($content);
    console.log( $users );

    // Add a button to each user.
    $users.each(function () {
        console.log( this );
        var $this = $( this ),
            $button = $( '<button>' )
                .addClass( 'oo-ui-buttonElement' )
                .text( mw.message( 'ping' ).plain() )
                .on( 'click', function () {
                    var $pre = $this.find( 'pre' ),
                        text = $pre.text();

                    if ( !$pre.length ) {
                        return;
                    }

                    try {
                        var result = eval( text );
                        if ( result !== undefined ) {
                            window.alert( result );
                        }
                    } catch ( e ) {
                        window.alert( e );
                    }
                } );

        $this.prepend( $button );
    } );
});
