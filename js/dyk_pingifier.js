"use strict";

// User:RoySmith/dyk-pingifier.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class Pingifier {
    constructor(mw) {
        this.mw = mw;
        this.updateTimes = {};
        this.$pingBox = null;
    }

    /**
     * 
     * @param {string} html UTF-8 encoded HTML from {{Did you know/Queue/LocalUpdateTimes}}
     * @return an object mapping queue/prep names to times
     */
    static parseLocalUpdateTimes(localUpdateTimes) {
        const queuePattern = new RegExp('(?<tag>Queue \\d)');
        const prepPattern = new RegExp('(?<tag>Prep \\d)');
        let updateTimes = {};
        $(localUpdateTimes).find('table.wikitable > tbody > tr').each(function ($row) {
            const $cells = $($(this).find('td'));
            if ($cells.length < 1) {
                return;
            }
            // This is ugly; it hard-wires that UTC is in column 3.  We really
            // should parse the table headers to see which is the right column.
            const time = $cells[3].innerHTML.replace('<br>', '&nbsp;').trim();
            const tags = $($cells[0]).text();
            var found = tags.match(queuePattern);
            if (found) {
                updateTimes[found.groups.tag] = time;
            }
            found = tags.match(prepPattern);
            if (found) {
                updateTimes[found.groups.tag] = time;
            }
        });
        return updateTimes;
    }

    async initializeLocalUpdateTimes() {
        const html = await $.get({ 'url': '/wiki/Template:Did_you_know/Queue/LocalUpdateTimes' });
        this.updateTimes = Pingifier.parseLocalUpdateTimes(html);
    }

    addPingBox() {
        this.$pingBox = $('<textarea id="ping-box" rows="8"></textarea>');
        this.$pingBox.insertBefore('#firstHeading');
        const templateName = $('#firstHeading > span.mw-page-title-main')
            .text()
            .replace('Did you know nominations/', '');
        this.$pingBox.append('===[[', this.mw.config.get('wgPageName'), '|', templateName, ']]===\n');
    }

    addCopyButton() {
        const $copyButton = $('<button id="copy-button">Copy</button>')
            .on('click', async function () {
                const $text = $('#ping-box').val();
                try {
                    await navigator.clipboard.writeText($text);
                    console.log('copied to clipboard', $text);
                } catch (error) {
                    console.log('Failed to copy!', error);
                    return;
                }
            });
        $copyButton.insertAfter('#ping-box');
    }

    addL2Button() {
        const $l2Button = $('<button id="l2-button">Add L2 Header</button>')
            .on('click', this, async function (event) {
                const params = {
                    action: 'query',
                    prop: 'linkshere',
                    titles: event.data.mw.config.get('wgPageName'),
                    format: 'json',
                };
                const api = new event.data.mw.Api();
                api.get(params)
                    .done(function (data) {
                        const id = event.data.mw.config.get('wgArticleId');
                        data.query.pages[id].linkshere.forEach(function (pageData) {
                            const title = pageData.title;
                            const titlePattern = new RegExp('^Template:Did you know/Queue/(?<n>\\d+)$');
                            const match = title.match(titlePattern);
                            if (match) {
                                const key = 'Queue ' + match.groups.n;
                                event.data.$pingBox.prepend('==[[', title, '|', key, ']] (', event.data.updateTimes[key], ')==\n\n');
                            };
                        })
                    });
            });
        $l2Button.insertAfter('#ping-box');
    }

    addPingButtons() {
        const userSubpagePattern = new RegExp('^/wiki/User:[^/]+$');
        const pingifier = this;
        const $userAnchors = $('div.mw-body-content a')
            .filter(function (index) {
                return userSubpagePattern.test($(this).attr('href'));
            });
        let processedUserNames = new Set();
        $userAnchors.each(function () {
            // It's unclear what adds the '#top' to some usernames.  It appears to
            // have something to do with users who have not set a custom signature.
            const userName = decodeURI($(this).attr('href')
                .replace(/^\/wiki\/User:/, '')
                .replace(/#top$/, '')
                .replace(/_/g, ' '));
            if (!processedUserNames.has(userName)) {
                const $button = $('<button class="dyk-ping-button">')
                    .attr('data-username', userName)
                    .text('ping')
                    .on('click', async function () {
                        pingifier.$pingBox.append('{{ping|' + this.dataset.username + '}}\n');
                    });
                $button.insertAfter($(this));
                processedUserNames.add(userName);
            }
        });
    }

    async init() {
        await this.initializeLocalUpdateTimes();
        this.addPingBox();
        this.addCopyButton();
        this.addL2Button();
        this.addPingButtons();
    }
}

if (typeof (module) != 'undefined') {
    module.exports = { Pingifier };
}

mw.hook('wikipage.content').add(async function ($content) {
    if (mw.config.get('wgPageName').match(/^Template:Did_you_know_nominations\//)) {
        new Pingifier(mw).init();
    }
});
