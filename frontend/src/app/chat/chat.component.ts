import { Component } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { TopicDialogComponent } from '../topic-dialog/topic-dialog.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent {

  messages: string[] = [];
  userMessage: string = '';


  constructor(private service: ChatService, private dialog: MatDialog) { }

  input_text: string = '';

  prompt: string = '';
  istyping: boolean = false;
  isPlaying: boolean = false;


  topics = [
    {
      title: 'Тема 1',
      description: 'Краткое описание темы 1',
      fullResponse: "Да, **Weaviate** — это векторная база данных с открытым исходным кодом, разработанная для работы с векторными представлениями данных (embedding vectors). Она широко используется для поиска по векторным embeddings, которые представляют собой числовые представления текста, изображений и других данных, полученные с помощью моделей машинного обучения. Weaviate поддерживает различные интеграции с NLP-моделями и фреймворками, такими как OpenAI, Hugging Face и другие, что делает её популярным выбором для создания систем с поиском по смыслу (semantic search) и систем рекомендаций."
    },
    {
      title: 'Тема 2',
      description: 'Краткое описание темы 2',
      fullResponse: 'Полный ответ для темы 2. Эта тема охватывает различные аспекты, которые могут быть полезны для понимания.'
    },
    {
      title: 'Тема 3',
      description: 'Краткое описание темы 3',
      fullResponse: 'Полный ответ для темы 3. Здесь вы найдете информацию о ключевых моментах и значении темы 3.'
    },
    {
      title: 'Тема 4',
      description: 'Краткое описание темы 4',
      fullResponse: 'Полный ответ для темы 4. Эта тема включает в себя важные факты и данные, которые стоит учитывать.'
    },
    {
      title: 'Тема 5',
      description: 'Краткое описание темы 5',
      fullResponse: 'Полный ответ для темы 5. Узнайте больше о различных аспектах и значении темы 5.'
    },
    {
      title: 'Тема 6',
      description: 'Краткое описание темы 6',
      fullResponse: 'Полный ответ для темы 6. Здесь представлены основные идеи и выводы по теме 6.'
    }
  ];



  getDescription() {
    if (!this.input_text.trim() || this.isPlaying) {
      this.input_text = '';
      return;
    }
    // this.topics.push({
    //   title: this.input_text,
    //   description: 'Описание для ' + this.input_text,
    //   fullResponse: 'Полный ответ для темы 1'
    // });


    var reqBody = {"content": this.input_text}
    this.service.handle_post_requests(reqBody, 'agent/generate').subscribe(response => {          
      var answer = response['answer']
      console.log(answer);
    });

    this.input_text = '';
  }






  openDialog(title: string, fullResponse: string) {
    this.dialog.open(TopicDialogComponent, {
      data: { title, fullResponse }
    });
  }
}
