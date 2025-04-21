class DYKReviewTool {
    constructor() {
    }

    async install() {
        mw.util.addPortletLink(
            'p-cactions',
            '#',
            'Review',
            'ca-review',
            'Review hookset',
        );
    }
}

if (typeof (module) != 'undefined') {
    module.exports = { DYKReviewTool };
}

mw.hook('wikipage.content').add(async function ($content) {
    if (mw.config.get('wgPageName').match(/^Template:Did_you_know\/Queue\//)) {
        new DYKReviewTool().install();
    }
});