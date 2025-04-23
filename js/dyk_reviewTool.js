"use strict";

// User:RoySmith/dyk-pingifier.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

const { LocalUpdateTimes } = require('./localUpdateTimes');
const { HookSet } = require('./hookset');

class DYKReviewTool {
    constructor(lut, hookSet) {
        this.localUpdateTimes = lut;
        this.hookSet = hookSet;
    }

    static async install() {
        const link = mw.util.addPortletLink(
            'p-cactions',
            '#',
            'Review',
            'ca-review',
            'Review hookset',
        );
        $(link).on('click', DYKReviewTool.review);
    }

    static async review() {
        const lut = await LocalUpdateTimes.build();
        const pageTitle = mw.config.get('wgPageName').replace(/_/g, ' ');
        const hookSet = await HookSet.build(pageTitle);
        const rt = new DYKReviewTool(lut, hookSet);
        rt.addReviewBox();
    }

    addReviewBox() {
        const key = this.hookSet.key();
        const $reviewBox = $('<textarea id="dyk-review-box" rows="8"></textarea>')
            .append(`==[[${this.hookSet.title}|${key}]] (${this.localUpdateTimes.updateTimes[key]})==\n`)
            .insertBefore('#firstHeading');
        for (const hook of this.hookSet.hooks) {
            const firstTarget = hook.links[0].target;
            const nomTitle = this.hookSet.nominationMap.get(firstTarget);
            $reviewBox
                .append(`\n`)
                .append(`===${nomTitle} ([[Template:Did you know nominations/${nomTitle}|nom]]===\n`)
                .append(`${hook.text}\n`)
        }
    }
}

if (typeof (module) != 'undefined') {
    module.exports = { DYKReviewTool };
}

mw.hook('wikipage.content').add(async function ($content) {
    if (mw.config.get('wgPageName').match(/^Template:Did_you_know\/Queue\//)) {
        DYKReviewTool.install();
        DYKReviewTool.review(); // for testing
    }
});