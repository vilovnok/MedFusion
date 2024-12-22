import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { MatDialog } from '@angular/material/dialog';
import { DialogComponent } from '../dialog/dialog.component';
import { Router } from '@angular/router';
import { NgToastService } from 'ng-angular-popup';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  @ViewChild('chatbox') private chatbox!: ElementRef;

  constructor(
    private service: ChatService, 
    private dialog: MatDialog,
    private router: Router,
    private toaster: NgToastService
  ) { }

  istyping: boolean = false;
  isPlaye: boolean = false;

  ngOnInit(): void {
    this.checkToken();  
    const reqBody = {'user_id':this.service.getFromLS('user_id')}
    this.getMessage(reqBody);
  }

  input_text: string = '';
  public sleep = (ms: number): Promise<void> => { return new Promise((r) => setTimeout(r, ms)); }


  messages: { role: string; text: string; liked: boolean | null }[] = [
    {
      'role': 'ai',
      'text': 'Привет! Что вас интересует в домене med. ?',
      'liked': null 
    },
  ];

  addMessage(role: string, text: string, liked?: boolean): void {
    this.messages.push({ 'role': role, 'text': text, 'liked': liked !== undefined ? liked : null   });
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    this.chatbox.nativeElement.scrollTop = this.chatbox.nativeElement.scrollHeight;
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  async generate() {

    if (!this.input_text.trim()) {
      this.input_text = '';
      return;
    }
    if (!this.service.getFromLS('token')) { 
      this.showDialog('2');      
      return;
    }      

    const role = 'human';
    const human_text = this.input_text;
    this.addMessage(role, human_text)
  
    this.input_text = '';
    await this.sleep(2000);
    this.istyping = true;

    const reqBody = {      
      "text": human_text,
      "user_id": this.service.getFromLS('user_id')
    }

    this.service.handle_post_requests(reqBody, 'agent/generate').subscribe(async response => {

      await this.sleep(2000);
      this.istyping = false;

      console.log(response);
      const role = response['role']
      const bot_text = response['ai_text']
      const liked = response['liked']
      this.addMessage(role, bot_text, liked);

    }, async error => {
      await this.sleep(2000);
      const role = 'ai';
      const bot_text = 'Произошла ошибка при обработке вашего запроса. Пожалуйста, проверьте ваш токен.'
      this.addMessage(role, bot_text);
      this.istyping = false;
      this.isPlaye = false;
      this.service.rmFromLS('token');
    });
    this.input_text = '';
  }

  showDialog(text: string='') {
    
    const dialogRef = this.dialog.open(DialogComponent, {
      width: '300px',
      height: '360px',
      data: {'text':text}
    });

    dialogRef.afterClosed().subscribe((api_key: string) => {
      if (!api_key.trim()) { 
        this.showDialog('2');      
        return;
      }      
        const reqBody = { 
          "token": api_key,
          "user_id": this.service.getFromLS('user_id') 
        }
        this.getToken(reqBody);  
    });
  }

  checkToken() {
    const reqBody={'user_id':localStorage.getItem('user_id')}
    if (!this.service.getFromLS('user_id')){
      this.router.navigate(['reg']);
      return;
    }
    if (this.service.getFromLS('token')){
      this.isPlaye = true;
      return;
    }
    this.getToken(reqBody);
  }

  getToken(reqBody: any) {
    this.service.handle_post_requests(reqBody, 'agent/check-token').subscribe(response => {
      localStorage.setItem('token', response.token);
      this.isPlaye = true;
    },error => {      
        this.showDialog('2'); 
        this.service.rmFromLS('token');
      this.isPlaye = false;
    });
  }

  changeLike(reqBody: any) {
    this.service.handle_post_requests(reqBody, 'agent/liked').subscribe(response => {
      this.toaster.warning({
        detail: "Благодарность",
        summary: "Спасибо Вам за обратную связь 😊"
      });
      
    },error => {      
      
    });
  }


  getMessage(reqBody: any) {

    interface Message {
      user_id: number;
      ai_text?: string; 
      human_text?: string;
      created_at: string;
      liked?: boolean;
  }
    this.service.handle_post_requests(reqBody, 'agent/get-messages').subscribe(response => {
      console.log(response['messages'].posts)
      const sortedPosts = response['messages'].posts.sort((a: any, b: any) => {
        return a.id - b.id;
      });

      sortedPosts.forEach((message: Message) => {
        if (message.human_text) {
          this.addMessage('human', message.human_text.trim());
        }
        if (message.ai_text) {
          this.addMessage('ai', message.ai_text.trim(), message.liked);
        }
      });


    }, err => console.log(err));
  }


  onLike(item: any): void {
    item.liked = true;
    const reqBody = {'liked':item.liked , 'text':item.text, 'user_id':this.service.getFromLS('user_id')}
    this.changeLike(reqBody);
  }

  onDislike(item: any): void {
    item.liked = false;
    const reqBody = {'liked':item.liked , 'text':item.text, 'user_id':this.service.getFromLS('user_id')}
    this.changeLike(reqBody);
  }

}
