(function () {
  // Register a custom SearchBuilder condition type that only exposes the
  // "Equals" operator. Fields with search_builder_type="eq_only" will use
  // this instead of the default "string" type, which exposes many operators
  // (Contains, Starts with, etc.) that the backend cannot handle.
  function register() {
    if (typeof $.fn.dataTable === "undefined") {
      setTimeout(register, 10);
      return;
    }
    $.fn.dataTable.ext.searchBuilder.conditions["eq_only"] = {
      "=": {
        conditionName: function (dt) {
          return dt.i18n(
            "searchBuilder.conditions.string.equals",
            "Equals"
          );
        },
        init: function (that, fn, preDefined) {
          var el = $('<input type="text" class="form-control form-control-sm">');
          el.on("input.dtsb keypress.dtsb", function () {
            fn(that);
          });
          if (preDefined) {
            el.val(preDefined[0]);
          }
          return el;
        },
        inputValue: function (el) {
          return [el[0].val()];
        },
        isInputValid: function (el) {
          return el[0].val().length > 0;
        },
        search: function (value, comparison) {
          return value === comparison[0];
        },
      },
    };
  }
  register();
})();
