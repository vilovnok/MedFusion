import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { MatDialog } from '@angular/material/dialog';
import { DialogComponent } from '../dialog/dialog.component';
import { Router } from '@angular/router';
import { NgToastService } from 'ng-angular-popup';

import { DomSanitizer, SafeHtml } from '@angular/platform-browser';


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
    private toaster: NgToastService,
    private sanitizer: DomSanitizer
  ) { }


  istyping: boolean = false;
  isPlaye: boolean = false;


  ngOnInit(): void {    
    const reqBody = {'user_id':this.service.getFromLS('user_id')}
    this.getToken(reqBody);
    this.getMessage(reqBody);
  }

  input_text: string = '';
  public sleep = (ms: number): Promise<void> => { return new Promise((r) => setTimeout(r, ms)); }

  sanitizeText(text: string): SafeHtml {
    let formattedText = text.replace(
      /\[([^\]]+)\]\[(https?:\/\/[^\s]+)\]/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }

  messages: { role: string; text: string; liked: boolean | null; collapsibleText?: string; isCollapsed?: boolean; id?: number  }[] = [
    {
      'role': 'ai',
      'text': "Привет! Я MedFusion - твой персональный помощник по доказательной медицине.\n\nОсобенности:\n1) В моей базе данных содержатся только обзоры статей с сайта доказательной медицины [Cochrane Library][https://www.cochranelibrary.com/cdsr/table-of-contents], опубликованные с 2003 года по ноябрь 2024 года. В моей базе данных нет клинических рекомендаций, но я все равно постараюсь тебе помочь!\n2) Я умею отвечать на общие медицинские вопросы, а также искать информацию по конкретной статье (по точному названию или по ссылке на doi)\n3) В нашем диалоге я помню только последние три сообщения. Историю чата можно сбросить при нажатии кнопки clear \n4) По окончании диалога, пожалуйста оставьте обратную связь, нажав на 👍/👎",
      'liked': null,
    },
  ];


  toggleCollapse(index: number): void {
    const message = this.messages[index];
    if (message) {
      message.isCollapsed = !message.isCollapsed;
    }
  }


  addMessage(role: string, text: string, 
            liked?: boolean, isCollapsed?: boolean, 
            collapsibleText?: string, id?: number): void {

    this.messages.push({ 'role': role, 
      'text': text, 'liked': liked !== undefined ? liked : null, 
      'isCollapsed': isCollapsed, 
      'collapsibleText': collapsibleText,
      'id': id,
    });

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
    if (!localStorage.getItem('token') || localStorage.getItem('token') === undefined) { 
      this.showDialog('2');      
      return;
    }      

    const role = 'human';
    const human_text = this.input_text.trim();
    this.addMessage(role, human_text)
  
    this.input_text = '';
    await this.sleep(2000);
    this.istyping = true;

    const reqBody = {      
      "text": human_text,
      "user_id": localStorage.getItem('user_id')
    }

    this.service.handle_post_requests(reqBody, 'agent/generate').subscribe(async response => {
      
      await this.sleep(1000);
      this.istyping = false;
      const role = response['role']
      const ai_text = response['ai_text'].trim().slice(0, response['ai_text'].trim().indexOf('**Ссылки**'))
      const liked = response['liked']
      const metadata = response['full_metadata']
      const id = response['id']
      this.addMessage(role, ai_text, liked, true, metadata, id);
    }, async error => {
      
      await this.sleep(2000);
      const role = 'ai';
      const bot_text = 'Произошла ошибка при обработке вашего запроса. Пожалуйста, проверьте ваш токен.'
      this.addMessage(role, bot_text);
      this.istyping = false;
      this.isPlaye = false;
      localStorage.removeItem('token');
      this.showDialog('2');   
      this.input_text = ''
    });
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
        this.checkToken(reqBody);  
    });
  }
  checkToken(reqBody: any) {
    this.service.handle_post_requests(reqBody, 'agent/check-token').subscribe(response => {
      localStorage.setItem('token', response.token);
      this.isPlaye = true;
    },error => {      
        this.showDialog('2'); 
        localStorage.removeItem('token');
      this.isPlaye = false;
    });
  }

  getToken(reqBody: any){
    this.service.handle_post_requests(reqBody, 'agent/get-token').subscribe(response => {
      this.isPlaye = true;
      localStorage.setItem('token', response.token);
    },error => {      
      if (error.status === 400){
        this.showDialog('1'); 
        this.isPlaye = false;
      }
      if (error.status === 404){
        this.router.navigate(['reg']); 
        this.isPlaye = false;
      }

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
      id?: number
      user_id: number;
      ai_text?: string; 
      human_text?: string;
      created_at: string;
      liked?: boolean;
      full_metadata?: string;
  }
    this.service.handle_post_requests(reqBody, 'agent/get-messages').subscribe(response => {
      const sortedPosts = response['messages'].posts.sort((a: any, b: any) => {
        return a.id - b.id;
      });

      sortedPosts.forEach((message: Message) => {
        if (message.human_text) {
          this.addMessage('human', message.human_text.trim());
        }
        if (message.ai_text) {
          const ai_text = message.ai_text.trim().slice(0, message.ai_text.trim().indexOf('**Ссылки**'))
          this.addMessage('ai', ai_text, message.liked, true, message.full_metadata, message.id);
        }
      });
    }, err => {
      if (err.status === 404){
        this.router.navigate(['reg']);
      }
      
    });
  }


  onLike(item: any): void {
    item.liked = true;
    const reqBody = {'liked':item.liked , 'user_id':localStorage.getItem('user_id'), 'message_id':item.id}
    this.changeLike(reqBody);
  }

  onDislike(item: any): void {
    item.liked = false;
    const reqBody = {'liked':item.liked , 'user_id':localStorage.getItem('user_id'), 'message_id':item.id}
    this.changeLike(reqBody);
  }


  clearChat() {    
    const reqBody = {'user_id': this.service.getFromLS('user_id')}
    this.service.handle_post_requests(reqBody, 'agent/clear-chat').subscribe(response => {
      window.location.reload();
    });
  }



  OpinionDialog(id: number=0) {
    console.log(id);
    const dialogRef = this.dialog.open(DialogComponent, {
      width: '300px',
      height: '360px',
      data: {'text':'3'}
    });

    dialogRef.afterClosed().subscribe((opinion: string) => {
      if (!opinion.trim()) { 
        this.showDialog('2');      
        return;
      }      
        const reqBody = { 
          "opinion": opinion,
          "user_id": localStorage.getItem('user_id') ,
          "message_id":id
        }
        this.service.handle_post_requests(reqBody, 'agent/add-opinion').subscribe(response => {

        });
        
    });
  }
}
