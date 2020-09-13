#!/usr/bin/env node

'use strict';
var Airtable = require('airtable');
var fs = require('fs');
var destination = process.argv[3]

var single = process.argv[2];

try {
  var base = new Airtable({apiKey: process.env.APIKEY}).base(process.env.BASE);

  base('🍩 Oral Histories').select({
      view: "Archival View (Comprehensive)",
      cellFormat: "string",
      timeZone: "America/New_York",
      userLocale: "en-ca",
      filterByFormula: "Identifier='"+single+"'",
  }).eachPage(function page(records, fetchNextPage) {
    if (!Array.isArray(records) || !!records.length) {
      records.forEach(function(record) {
          const content = [
            `Metadata for ${record.get('Identifier')}`,

            ...Object.keys(record.fields).map(field => `${field}: ${record.get(field)}`)
          ].join('\n');

          fs.writeFileSync(`${destination}/loctemp__${single}/${record.get('Identifier')}__metadata.txt`, content);
      });
      fetchNextPage();
    } else {
      console.log(`\x1b[31mWarning! ID '${single}' not found on airtable.`)
    }
  }, function done(err) {
      if (err) { 
        console.error(err); 
        return process.exit(1);
      }
  });
} catch (e) {
  console.error(e);
  return process.exit(1);
}