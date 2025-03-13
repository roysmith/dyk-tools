"use strict";

// User:RoySmith/dyk-pingifier.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class Pingifier {
    constructor(mw) {
        this.mw = mw;
        this.updateTimes = {};
    }

    /**
     * @param {string} html UTF-8 encoded HTML from {{Did you know/Queue/LocalUpdateTimes}}
     * @return an object mapping queue/prep names to times
     */
    static parseLocalUpdateTimes(localUpdateTimes) {
        let updateTimes = {};
        $(localUpdateTimes).find('table.wikitable > tbody > tr').each(function () {
            const $cells = $(this).find('td');
            if ($cells.length < 1) {
                // This will happen on the header row.
                return;
            }
            // This is ugly; it hard-wires that UTC is in column 3.  We really
            // should parse the table headers to see which is the right column.
            const time = $cells[3].innerHTML.replace('<br>', '&nbsp;').trim();
            const tags = $($cells[0]).text();
            const patterns = [
                /(?<tag>Queue \d)/,
                /(?<tag>Prep \d)/,
            ];
            patterns.forEach(function (pattern) {
                const found = tags.match(pattern);
                if (found) {
                    updateTimes[found.groups.tag] = time;
                }
            })
        });
        return updateTimes;
    }

    async initializeLocalUpdateTimes() {
        const html = await $.get({ 'url': '/wiki/Template:Did_you_know/Queue/LocalUpdateTimes' });
        this.updateTimes = Pingifier.parseLocalUpdateTimes(html);
    }

    addPingBox() {
        const $pingBox = $('<textarea id="dyk-ping-box" rows="8"></textarea>');
        $pingBox.insertBefore('#firstHeading');
        const templateName = $('#firstHeading > span.mw-page-title-main')
            .text()
            .replace('Did you know nominations/', '');
        $pingBox.append('===[[', this.mw.config.get('wgPageName'), '|', templateName, ']]===\n');
    }

    addCopyButton() {
        const $copyButton = $('<button id="copy-button">Sign and Copy</button>')
            .on('click', async function () {
                const $text = $('#dyk-ping-box')
                    .append('~~~~')
                    .val();
                try {
                    await navigator.clipboard.writeText($text);
                    console.log('copied to clipboard', $text);
                } catch (error) {
                    console.log('Failed to copy!', error);
                    return;
                }
            });
        $copyButton.insertAfter('#dyk-ping-box');
    }

    addL2Button() {
        const $l2Button = $('<button id="l2-button">Add L2 Header</button>')
            .on('click', this, async function (event) {
                const params = {
                    action: 'query',
                    prop: 'linkshere',
                    titles: event.data.mw.config.get('wgPageName'),
                    format: 'json',
                    lhnamespace: 10,  // Template namespace, TODO: don't hardwire number
                };
                const api = new event.data.mw.Api();
                api.get(params)
                    .then(function (data) {
                        const id = event.data.mw.config.get('wgArticleId');
                        data.query.pages[id].linkshere.forEach(function (pageData) {
                            const title = pageData.title;
                            const titlePattern = new RegExp('^Template:Did you know/Queue/(?<n>\\d+)$');
                            const match = title.match(titlePattern);
                            if (match) {
                                const key = 'Queue ' + match.groups.n;
                                $('#dyk-ping-box').prepend('==[[', title, '|', key, ']] (', event.data.updateTimes[key], ')==\n\n');
                            };
                        })
                    });
            });
        $l2Button.insertAfter('#dyk-ping-box');
    }

    /**
     * @param {jquery} $anchor <a> element linking to a user.
     * @return {string} the username.
     */
    getUserName($anchor) {
        // It's unclear what adds the '#top' to some usernames.  It appears to
        // have something to do with users who have not set a custom signature.
        return decodeURI($anchor.attr('href')
            .replace(/^\/wiki\/User:/, '')
            .replace(/#top$/, '')
            .replace(/_/g, ' '));
    }

    /**
     * @param (jquery) $anchor <a> element linking to a user.
     * @return (string) The user's role (promoter, nominator, approver), or null
     */
    classifyUser($anchor) {
        if ($anchor.closest('p').text().match(/promoted +by/)) {
            return "promoter";
        }
        if ($anchor.closest('p, li')
            .find('a[href*="Symbol_confirmed.svg"], a[href*="Symbol_voting_keep.svg"]')
            .length > 0) {
            return "approver";
        }
        // It is (probably) important that check comes last.  It's not clear
        // if parent() is the correct traversal to use here, but closest()
        // is definitely too large and leads to false positives.
        if ($anchor.parent('div').text().match(/nominations/)) {
            return "nominator";
        }
        return null;
    }

    /**
     * @param (jquery) $userAnchors all the <a> elements which link to users
     * @return a Map of usernames to roles as returned by classifyUser().
     */
    classifyAllUsers($userAnchors) {
        const userRoles = new Map();
        const pingifier = this;
        $userAnchors.each(function () {
            const username = pingifier.getUserName($(this));
            const role = pingifier.classifyUser($(this));
            if (role) {
                if (userRoles.has(username)) {
                    console.log('username(',
                        username,
                        ') already mapped to "',
                        userRoles.get(username),
                        '", ignoring attempt to remap it to "',
                        role,
                        '"');
                } else {
                    userRoles.set(username, role);
                }
            }
        });
        return userRoles;
    }

    findUserAnchors() {
        return $('div.mw-body-content a')
            .filter(function () {
                return $(this).attr('href').match(/^\/wiki\/User:[^/]+$/);
            });
    }

    addPingButtons() {
        const pingifier = this;
        const $userAnchors = this.findUserAnchors();
        const userRoles = this.classifyAllUsers($userAnchors);
        let processedUserNames = new Set();
        $userAnchors.each(function () {
            const userName = pingifier.getUserName($(this));
            if (!processedUserNames.has(userName)) {
                const $button = $('<button class="dyk-ping-button">')
                    .attr('data-username', userName)
                    .text('ping')
                    .on('click', async function () {
                        $('#dyk-ping-box').append('{{ping|' + this.dataset.username + '}}\n');
                    });
                const userRole = userRoles.get(userName);
                if (userRole) {
                    $button.addClass("dyk-" + userRole);
                }
                $button.insertAfter($(this));
                processedUserNames.add(userName);
            }
        });
    }

    addPingDefaultButton() {
        const pingifier = this;
        const usernames = $('button.dyk-promoter, button.dyk-nominator, button.dyk-approver')
            .map(function () {
                return $(this).data('username');
            })
            .get()
            .join('|');
        const $pingDefaultButton = $('<button id="ping-default-button">Ping Default</button>')
            .on('click', async function () {
                $('#dyk-ping-box').append('{{ping|' + usernames + '}}\n');
            });
        $pingDefaultButton.insertAfter('#dyk-ping-box');
    }

    addPingAllButton() {
        const pingifier = this;
        const usernames = $('button.dyk-ping-button')
            .map(function () {
                return $(this).data('username');
            })
            .get()
            .join('|');
        const $pingAllButton = $('<button id="ping-all-button">Ping All</button>')
            .on('click', async function () {
                $('#dyk-ping-box').append('{{ping|' + usernames + '}}\n');
            });
        $pingAllButton.insertAfter('#dyk-ping-box');
    }

    async init() {
        await this.initializeLocalUpdateTimes();
        this.addPingButtons();
        this.addPingBox();
        this.addCopyButton();
        this.addL2Button();
        this.addPingAllButton();
        this.addPingDefaultButton();
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
