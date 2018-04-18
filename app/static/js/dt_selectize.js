(function( factory ){
    if ( typeof define === 'function' && define.amd ) {
        // AMD
        define( ['jquery', 'datatables', 'datatables-editor'], factory );
    }
    else if ( typeof exports === 'object' ) {
        // Node / CommonJS
        module.exports = function ($, dt) {
            if ( ! $ ) { $ = require('jquery'); }
            factory( $, dt || $.fn.dataTable || require('datatables') );
        };
    }
    else if ( jQuery ) {
        // Browser standard
        factory( jQuery, jQuery.fn.dataTable );
    }
}(function( $, DataTable ) {
'use strict';
 
 
if ( ! DataTable.ext.editorFields ) {
    DataTable.ext.editorFields = {};
}
 
var _fieldTypes = DataTable.Editor ?
    DataTable.Editor.fieldTypes :
    DataTable.ext.editorFields;
 
 
_fieldTypes.selectize = {
    _addOptions: function ( conf, options ) {
        var selectize = conf._selectize;
/*
        selectize.clearOptions();
        selectize.addOption( options );
        selectize.refreshOptions(false);*/
    },
  
    create: function ( conf ) {
        var container = $('<div/>');
        conf._input = $('<input/>')
                .attr( $.extend( {
                    id: conf.id
                }, conf.attr || {} ) )
            .appendTo( container );
  
        conf._input.selectize( $.extend( {
            delimiter: ',',
            persist: true,
            create: function(input) {
                console.log(input);
                return {
                    value: input,
                    text: input
                }
            }            
/*            valueField: 'value',
            labelField: 'label',
            searchField: 'label',
            dropdownParent: 'body'*/
        }, conf.opts ) );
 
        conf._selectize = conf._input[0].selectize;
/*        conf.options = [
          {label:'aaaa', value:'aaaa'},
          {label:'bbbb', value:'bbbb'},
          {label:'ccaa', value:'ccaa'},
        ];
        if ( conf.options) {
            _fieldTypes.selectize._addOptions( conf, conf.options);
        }*/
 
        // Make sure the select list is closed when the form is submitted
        this.on( 'preSubmit', function () {
            conf._selectize.close();
        } );
  
        return container[0];
    },
  
    get: function ( conf ) {
        return conf._selectize.getValue();
    },
  
    set: function ( conf, val ) {
        return conf._selectize.setValue( val );
    },
  
    enable: function ( conf ) {
        conf._selectize.enable();
        $(conf._input).removeClass( 'disabled' );
    },
  
    disable: function ( conf ) {
        conf._selectize.disable();
        $(conf._input).addClass( 'disabled' );
    },
  
    // Non-standard Editor methods - custom to this plug-in
    inst: function ( conf ) {
        return conf._selectize;
    },
 
    update: function ( conf, options ) {
        _fieldTypes.selectize._addOptions( conf, options );
    }
};
 
 
}));