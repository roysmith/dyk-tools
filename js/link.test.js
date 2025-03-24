"use strict";

const { describe } = require('node:test');
const { Link } = require('./link');

describe('build', () => {
    it('creates a plain link', () => {
        const link = Link.build('foo')
        expect(link.target).toEqual('foo');
        expect(link.title).toEqual('');
    });

    it('creates a piped link', () => {
        const link = Link.build('foo|bar');
        expect(link.target).toEqual('foo');
        expect(link.title).toEqual('bar');
    });

    it('strips brackets', () => {
        const link = Link.build('[[foo]]');
        expect(link.target).toEqual('foo');
        expect(link.title).toEqual('');
    });
});