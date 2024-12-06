import { Component, ViewChild, ElementRef, AfterViewChecked, OnInit } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { TopicDialogComponent } from '../topic-dialog/topic-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { delay, of } from 'rxjs';
import { DialogComponent } from '../dialog/dialog.component';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent   implements OnInit{
  @ViewChild('chatbox') private chatbox!: ElementRef;
  
  constructor(private service: ChatService, private dialog: MatDialog)  { }
  
  
  
  
  ngOnInit(): void {
    // this.openDialog('title','titi');
    this.showDialog();

  }



  
  input_text: string = '';
  public sleep = (ms: number): Promise<void> => { return new Promise((r) => setTimeout(r, ms)); }


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
      // this.topics.push(newTopic);
  
      // #TODO возварщать title и description из back
      const reqBody = { "content": this.input_text }
      this.service.handle_post_requests(reqBody, 'agent/retrieve-data').subscribe(async response => {
        await this.sleep(2000);
        newTopic.flashing = false;
        newTopic.fullResponse = response['description'];
        newTopic.title = response['title'];
      }, async error => {
        await this.sleep(2000);
        // const index = this.topics.indexOf(newTopic);
        // if (index > -1) this.topics.splice(index, 1);  
        
        const role = 'bot';
        const text = 'Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.'
        this.addMessage(role, text);
        console.log(error);
      });
    this.input_text = '';
  }

  checkNetwork(){}


  showDialog() {
    const dialogRef = this.dialog.open(DialogComponent, {
      width: '250px',
      data: {}
    });
  }


  openDialog(title: string, fullResponse: string) {
    this.dialog.open(TopicDialogComponent, {
      data: { title, fullResponse }
    });
  }




}
