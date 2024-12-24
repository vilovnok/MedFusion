import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ChatService } from '../services/chat.service';

@Component({
  selector: 'app-dialog',
  templateUrl: './dialog.component.html',
  styleUrls: ['./dialog.component.scss']
})
export class DialogComponent implements OnInit {
  

  ngOnInit():void {
    this.dialogText(this.data['text']);
  }

  api_key: string = '';
  di_text: string = '';
  title: string = '';
  opinion: boolean = false;
  label: string = '';
  action: string = '';

  constructor(public dialogRef: MatDialogRef<DialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  onClose(): void {
    this.dialogRef.close();
  }


  dialogText(text: string){
    if (text=='1'){
      this.di_text = "Если Вы не подключены к модели Mistrial. Пожалуйста, выполните подключение и дождитесь смены цвета на зеленый."
      this.title = "Подключение к модели"
      this.label = 'Ключ подключения'
      this.action = 'Подключиться'
    }
    else if(text=='2'){
      this.di_text = "Вы не подключены к модели Mistrial. Пожалуйста, выполните подключение и дождитесь смены цвета на зеленый."
      this.title = "Подключение к модели"
      this.label = 'Ключ подключения'
      this.action = 'Подключиться'
    }
    else {
      this.di_text = 'Поделитесь, пожалуйста, своим мнением о том, как агент ответил на ваш вопрос. Это поможет нам улучшить качество ответов!'
      this.title = "Мнение"
      this.opinion = true
      this.label = 'Ваше мнение'
      this.action = 'Отправить'
    }

  }
}






