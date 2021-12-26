define(['jquery', 'underscore', 'twigjs'], function ($, _, Twig) {
  var CustomWidget = function () {
    var self = this;

    this.getTemplate = _.bind(function (template, params, callback) {
      params = (typeof params == 'object') ? params : {};
      template = template || '';

      return this.render({
        href: '/templates/' + template + '.twig',
        base_path: this.params.path,
        v: this.get_version(),
        load: callback
      }, params);
    }, this);


    this.setFirstElemSelect = function (select, textSelect) {
      let id_0 = document.createElement('option');
      id_0.innerHTML = textSelect;
      select.appendChild(id_0)
    }
    this.clearInput = function (input) {
      input.value = "";
    }

    //Удалим подчиненные эулументы
    this.removeElement = function (parent) {
      if (parent != null) {
        while (parent.firstChild) {
          parent.removeChild(parent.lastChild)
        }
      }
    }

    this.changeDateRequest_1c = function (date, isInit = false) {

      //Удалим все элементы из списка докторов
      let doctorSelect = self.divDoctor.querySelector('select')
      if (!isInit) {
        self.clearInput(self.inputDoctor); //Очистим поле ввода
      }
      self.removeElement(doctorSelect)
      self.setFirstElemSelect(doctorSelect, 'Список врачей')

      let timeSelect = self.devTime.querySelector('select')
      if (!isInit) {
        self.clearInput(self.inputTime); //Очистим поле ввода
      }
      self.removeElement(timeSelect)
      self.setFirstElemSelect(timeSelect, 'Время записи')


      let dataTo1C = {
        "date": date,
        "token": "*",
      }

      let jsonFor1C = JSON.stringify(dataTo1C);

      self.requests_1c(jsonFor1C, 'API/get_doctor_time');

    }

    this.setTimeAndDoctor = function (dateFrom1C) {

      /*Ищем div врача*/
      let vrachSelect = self.divDoctor.querySelector('select');

      dateFrom1C['doctors'].forEach(elementVrach => {

        let selectDoctor = document.createElement('option');

        /*
        вырежем кусок из текста Врач["12:00"]
        */
        let nameDoctor = elementVrach.slice(0, elementVrach.indexOf('['));
        let timeDoctor = elementVrach.slice(elementVrach.indexOf('[') + 1, elementVrach.length - 1);

        selectDoctor.innerHTML = nameDoctor;
        selectDoctor.dataset.time_Doctor = timeDoctor;

        vrachSelect.appendChild(selectDoctor);

      });
    }

    this.requests_1c = function (jsonFor1C, url) {

      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'https://IP:PORT/' + url, true);
      xhr.onerror = function () {
        alert("Соединение с сервром 1С не установленно")
      };

      xhr.onload = function () {

        let dateFrom1C = JSON.parse(this.responseText);
        
        if (dateFrom1C['Error']) {
          alert("Ошибка обмена с 1С: " + dateFrom1C['Error']);
          return;
        }

        if (dateFrom1C['doctors']) {
          self.setTimeAndDoctor(dateFrom1C);
        }

        if (dateFrom1C['document']) {
          alert(dateFrom1C['document']);
        }


      }

      xhr.send(jsonFor1C);
    }



this.initElement = function () {

  let mainDiv = document.querySelector('.linked-forms__group-wrapper');

  //ВЫБОР ДНЯ СОБЫТИЯ
  let choiceDate = document.querySelector('input[name="CFV[642473]"');

  self.choiceDate = choiceDate;

  //ВРАЧ
  self.divDoctor = document.querySelector('[data-id="642475"]');
  self.inputDoctor = document.querySelector('input[name="CFV[642475]"');


  //ВРЕМЯ ЗАПИСИ
  self.devTime = document.querySelector('[data-id="642477"]');
  self.inputTime = document.querySelector('input[name="CFV[642477]"');

  //КНОПКА СОХРАНИТЬ В 1С
  if (mainDiv != null) {
    btn = document.createElement('input');
    btn.id = 'SaveTo1C';
    btn.type = 'button';
    btn.value = 'Зарегистрировать запись к врачу в 1с';
    btn.classList.add('button-input');

    btn.addEventListener('click', (e) => {
       //ВЫГРУЖАЕМ ДАННЫЕ В 1С
      self.upload_lead_to_1C();
    })

    mainDiv.appendChild(btn);

  }

  //ИЗМЕНЕИЕ ВРАЧА
  if (self.divDoctor != null | self.inputDoctor != null) {

    self.inputDoctor.readOnly = true;
    let selectVrach = document.createElement('SELECT');

    self.setFirstElemSelect(selectVrach, "Список врачей")

    self.divDoctor.appendChild(selectVrach)

    selectVrach.addEventListener('change', (e) => {
      let nameDoctor = e.target.options[e.target.selectedIndex];
      self.inputDoctor.value = nameDoctor.innerHTML;
      self.inputDoctor.dispatchEvent(new KeyboardEvent('input', { bubbles: true }));

      let timeSelect = self.devTime.querySelector('select');

      self.clearInput(self.inputTime)// Очистим выбранную дату

      //Удалить все подчиненные элементы
      self.removeElement(timeSelect)
      self.setFirstElemSelect(timeSelect, 'Время записи')

      let arTimes = nameDoctor.dataset.time_Doctor.split(',');

      arTimes.forEach(elemData => {
        let varTime = document.createElement('option')
        varTime.innerHTML = elemData;

        timeSelect.appendChild(varTime)
      })
    })

  }
  //ИЗМЕНЕИЕ ВРАЧА



  //ИЗМЕНЕИЕ ВРЕМЕНИ
  if (self.devTime != null | self.inputTime != null) {
    self.inputTime.readOnly = true;
    let selectTime = document.createElement('SELECT');

    self.setFirstElemSelect(selectTime, "Время записи")

    self.devTime.appendChild(selectTime)

    selectTime.addEventListener('change', (e) => {
      self.inputTime.value = e.target.options[e.target.selectedIndex].innerHTML
      self.inputTime.dispatchEvent(new KeyboardEvent('input', { bubbles: true }));

    })
  }
  //ИЗМЕНЕИЕ ВРЕМЕНИ

  if (choiceDate != null) {
    if (choiceDate.value != '') {

      self.changeDateRequest_1c(choiceDate.value, true);

    }
    choiceDate.addEventListener('change', (e) => {
      self.changeDateRequest_1c(e.target.value)
    })
  }



}

/* Проверка параметров перед отправкой на сервер 1С*/
this.validateParam = function (idLead) {

  if (idLead == null) {
    alert("id лида не найден выгрузка в 1с не возможна");
    return false;
  }

  if (self.choiceDate == null || self.choiceDate.value.length == 0) {
    alert("Дата записи не указана");
    return false;
  }

  if (self.inputDoctor == null || self.inputDoctor.value.length == 0) {
    alert("Врач не заполнен");
    return false;
  }

  if (self.inputTime == null | self.inputTime.value.length == 0) {
    alert("Время записи не заполнено");
    return false;
  }

  return true
}

/*Выгрузка документа в 1С*/
this.upload_lead_to_1C = function () {
  let tmpUrl = window.location.pathname;

  //Преобразуем URL в Массив из массива возьмен последнюю часть это и есть наш id лида
  let idLead = window.location.pathname.split('/')[window.location.pathname.split('/').length - 1]

  if (self.validateParam(idLead)) {

    self.createNewDocumet1C(idLead);
  }


}

this.createNewDocumet1C = function (idLead) {
	let customer = document.querySelector('input[name="CFV[642641]"').value;
	let blockTel = document.querySelector('.control-phone');
	
	let tel = ''
	if (blockTel != null){
		tel = blockTel.querySelector('input').value;
	}
	
	let genderKod = document.querySelector('input[name="CFV[642713]"').value;
	let dateofBirth = document.querySelector('input[name="CFV[95453]"').value;
	
	let dataTo1C = {
		"token": "*",
		"numberAmo": idLead,
		"date": self.choiceDate.value,
		"doctor": self.inputDoctor.value,
		"time": self.inputTime.value,
		"customer" : customer,
		"tel": tel,
		"gender": genderKod,
		"DateofBirth": dateofBirth
	}

	let jsonFor1C = JSON.stringify(dataTo1C);
	
  self.requests_1c(jsonFor1C, 'API/cretate_document');
}


this.callbacks = {
  render: function () {

    //console.log('render')
    self.initElement()

    return true;
  },
  init: _.bind(function () {
    //console.log('init');

    AMOCRM.addNotificationCallback(self.get_settings().widget_code, function (data) {
      //console.log(data)
    });

    return true;
  }, this),
  bind_actions: function () {


    return true;
  },

  onSave: function () {
    alert('Version 1.13');
    return true;
  },
  destroy: function () {

  },
  tasks: {
    //select taks in list and clicked on widget name
    selected: function () {
      //console.log('tasks');
    }
  },
  advancedSettings: _.bind(function () {
    var $work_area = $('#work-area-' + self.get_settings().widget_code),
      $save_button = $(
        Twig({ ref: '/tmpl/controls/button.twig' }).render({
          text: 'Сохранить',
          class_name: 'button-input_blue button-input-disabled js-button-save-' + self.get_settings().widget_code,
          additional_data: ''
        })
      ),
      $cancel_button = $(
        Twig({ ref: '/tmpl/controls/cancel_button.twig' }).render({
          text: 'Отмена',
          class_name: 'button-input-disabled js-button-cancel-' + self.get_settings().widget_code,
          additional_data: ''
        })
      );

    //console.log('advancedSettings');

    $save_button.prop('disabled', true);
    $('.content__top__preset').css({ float: 'left' });

    $('.list__body-right__top').css({ display: 'block' })
      .append('<div class="list__body-right__top__buttons"></div>');
    $('.list__body-right__top__buttons').css({ float: 'right' })
      .append($cancel_button)
      .append($save_button);

    self.getTemplate('advanced_settings', {}, function (template) {
      var $page = $(
        template.render({ title: self.i18n('advanced').title, widget_code: self.get_settings().widget_code })
      );

      $work_area.append($page);
    });
  }, self),

  onSalesbotDesignerSave: function (handler_code, params) {
    var salesbot_source = {
      question: [],
      require: []
    },
      button_caption = params.button_caption || "",
      button_title = params.button_title || "",
      text = params.text || "",
      number = params.number || 0,
      handler_template = {
        handler: "show",
        params: {
          type: "buttons",
          value: text + ' ' + number,
          buttons: [
            button_title + ' ' + button_caption,
          ]
        }
      };

    console.log(params);

    salesbot_source.question.push(handler_template);

    return JSON.stringify([salesbot_source]);
  },
};

return this;
};

return CustomWidget;
});