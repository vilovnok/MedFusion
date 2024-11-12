import { Component, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { TopicDialogComponent } from '../topic-dialog/topic-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { delay, of } from 'rxjs';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent {
  @ViewChild('chatbox') private chatbox!: ElementRef;
  
  constructor(private service: ChatService, private dialog: MatDialog) { }
  
  input_text: string = '';
  public sleep = (ms: number): Promise<void> => { return new Promise((r) => setTimeout(r, ms)); }


  topics = [
    {
      title: 'Тема 1',
      description: 'Краткое описание темы 1',
      fullResponse: "Да, **Weaviate** — это векторная база данных с открытым исходным кодом, разработанная для работы с векторными представлениями данных (embedding vectors). Она широко используется для поиска по векторным embeddings, которые представляют собой числовые представления текста, изображений и других данных, полученные с помощью моделей машинного обучения. Weaviate поддерживает различные интеграции с NLP-моделями и фреймворками, такими как OpenAI, Hugging Face и другие, что делает её популярным выбором для создания систем с поиском по смыслу (semantic search) и систем рекомендаций.",
      flashing: false
    },
    {
      title: 'Тема 2',
      description: 'Краткое описание темы 2',
      fullResponse: 'Полный ответ для темы 2. Эта тема охватывает различные аспекты, которые могут быть полезны для понимания.',
      flashing: false
    },
    {
      title: 'Тема 3',
      description: 'Краткое описание темы 3',
      fullResponse: 'Полный ответ для темы 3. Здесь вы найдете информацию о ключевых моментах и значении темы 3.',
      flashing: false
    },
    {
      title: 'Тема 4',
      description: 'Краткое описание темы 4',
      fullResponse: 'Полный ответ для темы 4. Эта тема включает в себя важные факты и данные, которые стоит учитывать.',
      flashing: false
    },
    {
      title: 'Тема 5',
      description: 'Краткое описание темы 5',
      fullResponse: 'Полный ответ для темы 5. Узнайте больше о различных аспектах и значении темы 5.',
      flashing: false
    },
    {
      title: 'Тема 6',
      description: 'Краткое описание темы 6',
      fullResponse: 'Полный ответ для темы 6. Здесь представлены основные идеи и выводы по теме 6.',
      flashing: false
    }
  ];

  messages = [
    {
      role: 'bot',
      text: 'Hello! What are you interested in about the med. domain?',
    },
  ];

  addMessage(role: string, text: string) {
    this.messages.push({role: role, text: text});
    this.scrollToBottom();
}

private scrollToBottom(): void {
  this.chatbox.nativeElement.scrollTop = this.chatbox.nativeElement.scrollHeight;
}

ngAfterViewChecked() {
  this.scrollToBottom();
}


  async getDescription() {
    if (!this.input_text.trim()) {
      this.input_text = '';
      return;
    }
      const role = 'human';
      const text = this.input_text;
      this.addMessage(role, text)

      const newTopic = {
        title: 'Новая Тема',
        description: this.input_text,
        fullResponse: '',
        flashing: true,
      }
      this.topics.push(newTopic);
  
      // #TODO возварщать title и description из back
      const reqBody = { "content": this.input_text }
      this.service.handle_post_requests(reqBody, 'agent/retrieve-data').subscribe(async response => {
        await this.sleep(2000);
        newTopic.flashing = false;
        newTopic.fullResponse = response['description'];
        newTopic.title = response['title'];
      }, async error => {
        await this.sleep(2000);
        const index = this.topics.indexOf(newTopic);
        if (index > -1) this.topics.splice(index, 1);  
        
        const role = 'bot';
        const text = 'Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.'
        this.addMessage(role, text);
        console.log(error);
      });
    this.input_text = '';
  }

// #TODO (создать get запрос для карточек)
  // getTopic() {
  //   var reqBody = { "content": this.input_text }
  //   this.service.handle_post_requests(reqBody, 'agent/retrieve-data').subscribe(response => {});
  // }

  openDialog(title: string, fullResponse: string) {
    this.dialog.open(TopicDialogComponent, {
      data: { title, fullResponse }
    });
  }
}
