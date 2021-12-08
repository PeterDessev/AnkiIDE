DEFAULT_CONFIG = {
  "user": {
    "html": "default",
    "css": "default"
  },
  "html": {
    "default": {
      "editing": {
        "tabs_to_spaces": True,
        "tab_width": 4
      },
      "style": {
        "tag_color": "#008080",
        "element_color": "#008000",
        "element_style": "bold",
        "attribute_color": "#7D9029",
        "equals_color": "#7D9029",
        "value_color": "#BA2121",
        "moustache_color": "#BC7A00",
        "moustache_style": "bold"
      }
    }
  },
  "css":  {
    "default": {
      "editing": {
        "tabs_to_spaces": True,
        "tab_width": 4
      },
      "style": {
        "brace_color": "#BB7977",
        "selector_color": "#800000",
        "selector_style": "bold",
        "property_color": "#BB7977",
        "property_style": "bold",
        "equals_color": "gray",
        "value_color": "#074726"
      }
    }
  },
  "font": "default"
}
# {
#   "name": "Monokai Night",
#   "type": "dark",
#   "colors": {
#   "tokenColors": [
#    {
#       "name": "String",
#       "scope": "string",
#       "settings": {
#         "foreground": "#E6DB74"
#       }
#     },
#     {
#       "name": "Template Definition",
#       "scope": [
#         "punctuation.definition.template-expression",
#         "punctuation.section.embedded"
#       ],
#       "settings": {
#         "foreground": "#F92672"
#       }
#     },
#     {
#       "name": "Reset JavaScript string interpolation expression",
#       "scope": [
#         "meta.template.expression"
#       ],
#       "settings": {
#         "foreground": "#F8F8F2"
#       }
#     },
#     {
#       "name": "Number",
#       "scope": "constant.numeric",
#       "settings": {
#         "foreground": "#AE81FF"
#       }
#     },
#     {
#       "name": "Built-in constant",
#       "scope": "constant.language",
#       "settings": {
#         "foreground": "#AE81FF"
#       }
#     },
#     {
#       "name": "User-defined constant",
#       "scope": "constant.character, constant.other",
#       "settings": {
#         "foreground": "#AE81FF"
#       }
#     },
#     {
#       "name": "Variable",
#       "scope": "variable",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#F8F8F2"
#       }
#     },
#     {
#       "name": "Keyword",
#       "scope": "keyword",
#       "settings": {
#         "foreground": "#F92672"
#       }
#     },
#     {
#       "name": "Storage",
#       "scope": "storage",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#F92672"
#       }
#     },
#     {
#       "name": "Storage type",
#       "scope": "storage.type",
#       "settings": {
#         "fontStyle": "italic",
#         "foreground": "#66D9EF"
#       }
#     },
#     {
#       "name": "Class name",
#       "scope": "entity.name.type, entity.name.class",
#       "settings": {
#         "fontStyle": "underline",
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "name": "Inherited class",
#       "scope": "entity.other.inherited-class",
#       "settings": {
#         "fontStyle": "italic underline",
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "name": "Function name",
#       "scope": "entity.name.function",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "name": "Function argument",
#       "scope": "variable.parameter",
#       "settings": {
#         "fontStyle": "italic",
#         "foreground": "#FD971F"
#       }
#     },
#     {
#       "name": "Tag name",
#       "scope": "entity.name.tag",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#F92672"
#       }
#     },
#     {
#       "name": "Tag attribute",
#       "scope": "entity.other.attribute-name",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "name": "Library function",
#       "scope": "support.function",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#66D9EF"
#       }
#     },
#     {
#       "name": "Library constant",
#       "scope": "support.constant",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#66D9EF"
#       }
#     },
#     {
#       "name": "Library class/type",
#       "scope": "support.type, support.class",
#       "settings": {
#         "fontStyle": "italic",
#         "foreground": "#66D9EF"
#       }
#     },
#     {
#       "name": "Library variable",
#       "scope": "support.other.variable",
#       "settings": {
#         "fontStyle": ""
#       }
#     },
#     {
#       "name": "Invalid",
#       "scope": "invalid",
#       "settings": {
#         "background": "#F92672",
#         "fontStyle": "",
#         "foreground": "#F8F8F0"
#       }
#     },
#     {
#       "name": "Invalid deprecated",
#       "scope": "invalid.deprecated",
#       "settings": {
#         "background": "#AE81FF",
#         "foreground": "#F8F8F0"
#       }
#     },
#     {
#       "name": "JSON String",
#       "scope": "meta.structure.dictionary.json string.quoted.double.json",
#       "settings": {
#         "foreground": "#CFCFC2"
#       }
#     },
#     {
#       "name": "diff.header",
#       "scope": "meta.diff, meta.diff.header",
#       "settings": {
#         "foreground": "#75715E"
#       }
#     },
#     {
#       "name": "diff.deleted",
#       "scope": "markup.deleted",
#       "settings": {
#         "foreground": "#F92672"
#       }
#     },
#     {
#       "name": "diff.inserted",
#       "scope": "markup.inserted",
#       "settings": {
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "name": "diff.changed",
#       "scope": "markup.changed",
#       "settings": {
#         "foreground": "#E6DB74"
#       }
#     },
#     {
#       "scope": "constant.numeric.line-number.find-in-files - match",
#       "settings": {
#         "foreground": "#AE81FFA0"
#       }
#     },
#     {
#       "scope": "entity.name.filename.find-in-files",
#       "settings": {
#         "foreground": "#E6DB74"
#       }
#     },
#     {
#       "name": "Markup Quote",
#       "scope": "markup.quote",
#       "settings": {
#         "foreground": "#F92672"
#       }
#     },
#     {
#       "name": "Markup Lists",
#       "scope": "markup.list",
#       "settings": {
#         "foreground": "#E6DB74"
#       }
#     },
#     {
#       "name": "Markup Styling",
#       "scope": "markup.bold, markup.italic",
#       "settings": {
#         "foreground": "#66D9EF"
#       }
#     },
#     {
#       "name": "Markup Inline",
#       "scope": "markup.inline.raw",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#FD971F"
#       }
#     },
#     {
#       "name": "Markup Headings",
#       "scope": "markup.heading",
#       "settings": {
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "name": "Markup Setext Header",
#       "scope": "markup.heading.setext",
#       "settings": {
#         "fontStyle": "",
#         "foreground": "#A6E22E"
#       }
#     },
#     {
#       "scope": "token.info-token",
#       "settings": {
#         "foreground": "#6796e6"
#       }
#     },
#     {
#       "scope": "token.warn-token",
#       "settings": {
#         "foreground": "#cd9731"
#       }
#     },
#     {
#       "scope": "token.error-token",
#       "settings": {
#         "foreground": "#f44747"
#       }
#     },
#     {
#       "scope": "token.debug-token",
#       "settings": {
#         "foreground": "#b267e6"
#       }
#     },
#     {
#       "name": "this.self",
#       "scope": "variable.language",
#       "settings": {
#         "foreground": "#FD971F"
#       }
#     }
#   ]
# }